"""
Endpoints del DRL - Motor de Recomendaciones con Integración a Backend
Solo recomendación de ejercicios + cálculo de rewards
Sin persistencia (manejada desde sheetmusic-backend)
"""

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional, Dict
import numpy as np
import random
import logging
from datetime import datetime

from ia_drl_engine.src.agents.load_agent import get_model
from ia_drl_engine.src.utils.skill_mapping import load_skill_mapping
from ia_drl_engine.src.agents.inference import (
    state_to_observation,
    calculate_difficulty,
    GENERATOR_MAP
)
from ia_drl_engine.src.utils.activation import get_enabled_nodes, set_node_enabled

# ============= LOGGING =============
logger = logging.getLogger(__name__)

# ============= MODELOS PYDANTIC =============

class StudentState(BaseModel):
    skill_proficiency: Dict[str, float]
    preferred_node: Optional[str] = None
    difficulty: Optional[int] = None
    free_navigation: bool = True


class FocusNodes(BaseModel):
    nodes: List[str]
    strict: bool = False


class NextExerciseRequest(BaseModel):
    student_id: str  # ← NUEVO: ID del estudiante
    student_state: StudentState
    focus: Optional[FocusNodes] = None


class SessionEvent(BaseModel):
    node: str
    correct: bool
    response_time: int
    difficulty: int


class SessionEndRequest(BaseModel):
    student_id: str  # ← NUEVO: ID del estudiante
    session_events: List[SessionEvent]


# ============= EXPERIENCE BUFFER (EN MEMORIA) =============
# En producción, esto se guardaría en BD desde el backend
experience_buffer: List[Dict] = []
MAX_BUFFER_SIZE = 1000


class ExperienceBuffer:
    """Guarda experiencias en memoria para entrenar"""

    @staticmethod
    def add_experience(student_id: str, experience: Dict):
        """Agrega experiencia al buffer"""
        global experience_buffer

        experience["student_id"] = student_id
        experience["timestamp"] = datetime.now().isoformat()

        experience_buffer.append(experience)

        # Mantener tamaño máximo
        if len(experience_buffer) > MAX_BUFFER_SIZE:
            experience_buffer.pop(0)

        logger.info(
            f"Added experience for {student_id}. Buffer size: {len(experience_buffer)}"
        )

    @staticmethod
    def get_student_experiences(student_id: str, limit: int = 100) -> List[Dict]:
        """Obtiene experiencias de un estudiante específico"""
        return [
            exp
            for exp in experience_buffer
            if exp.get("student_id") == student_id
        ][-limit:]

    @staticmethod
    def clear():
        """Limpia el buffer (útil después de entrenar)"""
        global experience_buffer
        experience_buffer.clear()


# ============= FUNCIONES DE LÓGICA =============


def predict_with_focus(
    model, student_state_dict: Dict, focus_nodes=None, strict=False
):
    """
    Predice el siguiente ejercicio con soporte para focus nodes

    Args:
        model: Modelo PPO cargado
        student_state_dict: Estado actual del estudiante
        focus_nodes: Nodos en los que enfocarse (opcional)
        strict: Si True, SIEMPRE elige de focus_nodes. Si False, preferencia flexible

    Returns:
        Dict con recomendación
    """
    try:
        obs = state_to_observation(student_state_dict)
        action, _ = model.predict(obs, deterministic=True)

        _, idx_to_skill, _ = load_skill_mapping()
        selected_skill = idx_to_skill[int(action)]

        # Preparar lista de nodos habilitados respetando el orden de GENERATOR_MAP
        enabled = get_enabled_nodes()
        enabled_list = [s for s in GENERATOR_MAP.keys() if s in enabled]
        if not enabled_list:
            # No hay nodos habilitados: dejar la selección del modelo (pero avisar)
            logger.warning("No enabled nodes found in activation.json; falling back to model selection")


        # Aplicar lógica de focus (respetando sólo nodos habilitados)
        if focus_nodes:
            proficiencies = student_state_dict.get("skill_proficiency", {})
            # Preferir focus nodes que además estén habilitados
            focus_enabled = [n for n in focus_nodes if n in enabled_list]

            if strict:
                # Modo estricto: SIEMPRE en focus (pero sólo nodos habilitados)
                if focus_enabled:
                    weakest = min(focus_enabled, key=lambda n: proficiencies.get(n, 0))
                    selected_skill = weakest
                    logger.info(f"Strict focus applied (enabled): {selected_skill}")
                else:
                    # Ningún focus habilitado: elegir aleatoriamente entre habilitados
                    if enabled_list:
                        selected_skill = random.choice(enabled_list)
                        logger.info(
                            "Strict focus requested but no focus nodes enabled; falling back to random enabled node"
                        )
            else:
                # Modo flexible: prefiere focus si está muy débil (considerando habilitados)
                candidates = focus_enabled if focus_enabled else [n for n in focus_nodes if n in GENERATOR_MAP]
                if candidates and selected_skill not in candidates:
                    focus_profs = {n: proficiencies.get(n, 0) for n in candidates}
                    weakest_focus = min(focus_profs, key=focus_profs.get)
                    if proficiencies.get(weakest_focus, 0) < proficiencies.get(selected_skill, 0.5):
                        selected_skill = weakest_focus
                        logger.info(f"Flexible focus applied: {selected_skill}")

        # Asegurarnos de nuevo que la selección final esté entre los habilitados
        if enabled_list and selected_skill not in enabled_list:
            selected_skill = random.choice(enabled_list)
            logger.info(f"Selected skill was disabled; falling back to enabled: {selected_skill}")

        difficulty = calculate_difficulty(student_state_dict, selected_skill)
        generator = GENERATOR_MAP.get(selected_skill, GENERATOR_MAP["1a"])
        exercise = generator(difficulty=difficulty)

        return {
            "recommended_node": selected_skill,
            "difficulty": difficulty,
            "exercise": exercise,
            "focus_applied": selected_skill in (focus_nodes or []),
        }
    except Exception as e:
        logger.error(f"Error in predict_with_focus: {e}")
        raise


def calculate_session_reward(events_data: List[SessionEvent]) -> Dict:
    """
    Calcula recompensa total y proficiencia actualizada de una sesión

    Fórmula de reward por evento:
    - Base: 1.0 si correcto, 0.0 si incorrecto
    - Bonus dificultad: +0.5 si óptima, -0.3 si muy difícil/fácil
    - Bonus tiempo: +0.2 si razonable, -0.1 si muy lento
    """
    total_reward = 0.0
    node_rewards = {}
    updated_proficiency = {}
    success_count = 0

    for event in events_data:
        node = event.node
        correct = event.correct
        difficulty = event.difficulty
        response_time = event.response_time

        # ① BASE: ¿Acertó?
        reward = 1.0 if correct else 0.0

        # ② BONUS DIFICULTAD (óptima es 2-3)
        if 2 <= difficulty <= 3:
            reward += 0.5
        elif difficulty > 4:
            reward -= 0.3  # Muy difícil
        elif difficulty < 1:
            reward -= 0.2  # Muy fácil

        # ③ BONUS TIEMPO RESPUESTA (ideal 5-15 segundos)
        if 3000 <= response_time <= 15000:
            reward += 0.2
        elif response_time > 30000:
            reward -= 0.1  # Demasiado tiempo

        # Acumular
        total_reward += reward
        node_rewards[node] = node_rewards.get(node, 0) + reward

        # ④ ACTUALIZAR PROFICIENCIA
        if node not in updated_proficiency:
            updated_proficiency[node] = 0.0

        if correct:
            updated_proficiency[node] = min(
                1.0, updated_proficiency[node] + 0.05
            )
            success_count += 1
        else:
            updated_proficiency[node] = max(
                -0.2, updated_proficiency[node] - 0.02
            )

    # Promediar rewards por nodo (si hay múltiples)
    node_rewards_avg = {}
    for node, reward in node_rewards.items():
        count = sum(1 for e in events_data if e.node == node)
        node_rewards_avg[node] = round(reward / count if count > 0 else 0, 2)

    success_rate = (
        round(success_count / len(events_data), 3)
        if events_data
        else 0.0
    )

    return {
        "total_reward": round(total_reward, 2),
        "node_rewards": node_rewards_avg,
        "updated_proficiencies": {
            k: round(v, 3) for k, v in updated_proficiency.items()
        },
        "success_rate": success_rate,
        "events_count": len(events_data),
        "success_count": success_count,
    }



def recommend_next_nodes(
    proficiencies: Dict[str, float], count: int = 3
) -> List[str]:
    """Recomienda los próximos nodos a practicar (los más débiles)"""
    sorted_nodes = sorted(proficiencies.items(), key=lambda x: x[1])
    return [node for node, _ in sorted_nodes[:count]]


# ============= ENDPOINTS =============


def setup_endpoints(app: FastAPI):
    """Registra los endpoints en la app FastAPI"""

    async def _log_request_body(req: Request) -> dict:
        """Read and return raw and parsed JSON body for logging.

        Returns a dict with keys: raw, parsed (or None if not JSON)
        """
        try:
            raw = await req.body()
            raw_text = raw.decode('utf-8') if isinstance(raw, (bytes, bytearray)) else str(raw)
        except Exception:
            raw_text = '<unreadable body>'

        parsed = None
        try:
            parsed = await req.json()
        except Exception:
            parsed = None

        return {"raw": raw_text, "parsed": parsed}


    @app.post("/next-exercise")
    async def next_exercise(req: Request):
        """
        Recomienda el siguiente ejercicio basado en proficiencia del estudiante

        Con soporte opcional para focus nodes

        Args:
            student_id: ID del estudiante (para logging/tracking)
            student_state: Estado actual del estudiante
            focus: Opcional - restricción de nodos

        Returns:
            Recomendación de ejercicio
        """
        # Log raw and parsed body for debugging
        body_info = await _log_request_body(req)
        logger.info(f"[NextExercise] Raw body: {body_info['raw']}")
        logger.info(f"[NextExercise] Parsed body: {body_info['parsed']}")

        try:
            # Validate and parse using Pydantic model
            payload = NextExerciseRequest.parse_obj(body_info['parsed'] or {})
            student_id = payload.student_id
            logger.info(f"[NextExercise] Student: {student_id}")

            model = get_model()
            state_dict = payload.student_state.dict()

            focus_config = payload.focus
            focus_nodes = focus_config.nodes if focus_config else None
            strict = focus_config.strict if focus_config else False

            recommendation = predict_with_focus(
                model,
                state_dict,
                focus_nodes=focus_nodes,
                strict=strict,
            )

            logger.info(f"[NextExercise] Recommended: {recommendation['recommended_node']}")

            return {
                "status": "success",
                "recommended_node": recommendation["recommended_node"],
                "difficulty": recommendation["difficulty"],
                "exercise": recommendation["exercise"],
                "focus_applied": recommendation["focus_applied"],
            }

        except Exception as e:
            logger.exception(f"[NextExercise] Error while processing request")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/session-end")
    async def session_end(req: Request):
        """
        Calcula recompensa y proficiencia actualizada de una sesión

        NO persiste datos (eso lo hace sheetmusic-backend)
        Pero SÍ guarda en buffer para futuro entrenamiento

        Args:
            student_id: ID del estudiante
            session_events: Lista de eventos de la sesión

        Returns:
            Rewards, proficiencias actualizadas, recomendaciones
        """
        # Log body
        body_info = await _log_request_body(req)
        logger.info(f"[SessionEnd] Raw body: {body_info['raw']}")
        logger.info(f"[SessionEnd] Parsed body: {body_info['parsed']}")

        try:
            payload = SessionEndRequest.parse_obj(body_info['parsed'] or {})
            student_id = payload.student_id
            session_events = payload.session_events

            if not session_events:
                raise HTTPException(status_code=400, detail="No session events provided")

            logger.info(f"[SessionEnd] Processing {len(session_events)} events for {student_id}")

            # 1) Calcular rewards
            result = calculate_session_reward(session_events)

            # 2) Guardar en buffer para entrenar despues
            experience = {
                "events": [e.dict() for e in session_events],
                "total_reward": result["total_reward"],
                "node_rewards": result["node_rewards"],
                "success_rate": result["success_rate"],
            }
            ExperienceBuffer.add_experience(student_id, experience)

            # 3) Generar recomendaciones
            recommendations = recommend_next_nodes(result["updated_proficiencies"]) 

            logger.info(f"[SessionEnd] Total reward: {result['total_reward']}, Success rate: {result['success_rate']}")

            training_triggered = (len(experience_buffer) >= 32)

            return {
                "status": "success",
                "total_reward": result["total_reward"],
                "node_rewards": result["node_rewards"],
                "updated_proficiencies": result["updated_proficiencies"],
                "success_rate": result["success_rate"],
                "next_recommendations": recommendations,
                "drl_training_triggered": training_triggered,
                "buffer_size": len(experience_buffer),
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.exception("[SessionEnd] Error while processing request")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/student-analytics/{student_id}")
    async def get_student_analytics(student_id: str):
        """
        Obtiene análisis del estudiante desde experiencias en buffer

        Nota: En producción, esto vendría de la BD
        """
        try:
            logger.info(f"[Analytics] Fetching for {student_id}")

            experiences = ExperienceBuffer.get_student_experiences(student_id)

            if not experiences:
                return {
                    "status": "success",
                    "student_id": student_id,
                    "data": {
                        "sessions_count": 0,
                        "average_reward": 0.0,
                        "average_success_rate": 0.0,
                        "proficiencies": {},
                    },
                }

            # Calcular promedios
            avg_reward = np.mean(
                [e.get("total_reward", 0) for e in experiences]
            )
            avg_success_rate = np.mean(
                [e.get("success_rate", 0) for e in experiences]
            )

            # Último proficiency conocido
            last_proficiencies = (
                experiences[-1].get("updated_proficiencies", {})
                if experiences
                else {}
            )

            return {
                "status": "success",
                "student_id": student_id,
                "data": {
                    "sessions_count": len(experiences),
                    "average_reward": round(float(avg_reward), 2),
                    "average_success_rate": round(float(avg_success_rate), 3),
                    "proficiencies": last_proficiencies,
                },
            }

        except Exception:
            logger.exception("[Analytics] Error while fetching analytics")
            raise HTTPException(status_code=500, detail="Failed to fetch analytics")

    @app.get("/activation/list")
    async def list_activation():
        """Lista nodos habilitados por el activador (activation.json o graph default)"""
        enabled = sorted(list(get_enabled_nodes()))
        return {"status": "success", "enabled": enabled}


    class ActivationToggle(BaseModel):
        node_id: str
        enabled: bool

    @app.post("/activation/toggle")
    async def toggle_activation(req: Request):
        body_info = await _log_request_body(req)
        logger.info(f"[ActivationToggle] Raw body: {body_info['raw']}")
        logger.info(f"[ActivationToggle] Parsed body: {body_info['parsed']}")

        try:
            payload = ActivationToggle.parse_obj(body_info['parsed'] or {})
            set_node_enabled(payload.node_id, payload.enabled)
            return {"status": "success", "node": payload.node_id, "enabled": payload.enabled}
        except Exception:
            logger.exception("[ActivationToggle] Error while processing request")
            raise HTTPException(status_code=400, detail="Invalid activation toggle payload")

    @app.get("/health")
    async def health_check():
        """Health check del DRL Engine"""
        try:
            model = get_model()
            return {
                "status": "healthy",
                "model_loaded": model is not None,
                "buffer_size": len(experience_buffer),
            }
        except Exception:
            logger.exception("[Health] Error while checking health")
            raise HTTPException(status_code=500, detail="DRL engine unhealthy")

    @app.get("/model-version")
    async def get_model_version():
        """Obtiene versión del modelo actual"""
        try:
            # En producción, esto vendría de metadata del modelo
            return {
                "version": "1.0.0",
                "model_type": "PPO",
                "last_trained": "2026-05-10",
            }
        except Exception:
            logger.exception("[ModelVersion] Error while getting model version")
            raise HTTPException(status_code=500, detail="Failed to get model version")
