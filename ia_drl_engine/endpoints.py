"""
Endpoints del DRL - Solo recomendación de ejercicios con focus nodes
Sin persistencia (manejada desde otro backend)
"""

from pydantic import BaseModel
from typing import List, Optional, Dict
import numpy as np

from ia_drl_engine.src.agents.load_agent import get_model
from ia_drl_engine.src.utils.skill_mapping import load_skill_mapping
from ia_drl_engine.src.agents.inference import (
    state_to_observation,
    calculate_difficulty,
    GENERATOR_MAP
)


# ============= MODELOS =============

class StudentState(BaseModel):
    skill_proficiency: Dict[str, float]
    preferred_node: Optional[str] = None
    difficulty: Optional[int] = None
    free_navigation: bool = True


class FocusNodes(BaseModel):
    nodes: List[str]
    strict: bool = False


class NextExerciseRequest(BaseModel):
    student_state: StudentState
    focus: Optional[FocusNodes] = None


class SessionEvent(BaseModel):
    node: str
    correct: bool
    response_time: int
    difficulty: int


class SessionEndRequest(BaseModel):
    session_events: List[SessionEvent]


# ============= FUNCIONES =============

import torch


def predict_with_focus(model, student_state_dict, focus_nodes=None, strict=False):
    """
    Predice el siguiente ejercicio con soporte para focus nodes
    """
    obs = state_to_observation(student_state_dict)
    # Use inference_mode to lower memory usage and ensure no grads are tracked
    with torch.inference_mode():
        action, _ = model.predict(obs, deterministic=True)
    
    _, idx_to_skill, _ = load_skill_mapping()
    selected_skill = idx_to_skill[int(action)]
    
    # Aplicar lógica de focus
    if focus_nodes:
        if strict:
            # Modo estricto: SIEMPRE en focus
            proficiencies = student_state_dict.get('skill_proficiency', {})
            weakest = min(
                focus_nodes,
                key=lambda n: proficiencies.get(n, 0)
            )
            selected_skill = weakest
        else:
            # Modo flexible: prefiere focus si está muy débil
            proficiencies = student_state_dict.get('skill_proficiency', {})
            if selected_skill not in focus_nodes:
                focus_profs = {
                    n: proficiencies.get(n, 0) 
                    for n in focus_nodes
                }
                weakest_focus = min(focus_profs, key=focus_profs.get)
                if proficiencies.get(weakest_focus, 0) < proficiencies.get(selected_skill, 0.5):
                    selected_skill = weakest_focus
    
    difficulty = calculate_difficulty(student_state_dict, selected_skill)
    generator = GENERATOR_MAP.get(selected_skill, GENERATOR_MAP["1a"])
    exercise = generator(difficulty=difficulty)
    
    return {
        "recommended_node": selected_skill,
        "difficulty": difficulty,
        "exercise": exercise,
        "focus_applied": selected_skill in (focus_nodes or [])
    }


def calculate_session_reward(events_data: List[SessionEvent]):
    """
    Calcula recompensa y proficiencia actualizada de una sesión
    """
    total_reward = 0.0
    node_rewards = {}
    updated_proficiency = {}
    
    for event in events_data:
        node = event.node
        correct = event.correct
        difficulty = event.difficulty
        
        # Recompensa por evento
        correctness = 1.0 if correct else -0.5
        difficulty_bonus = (difficulty - 1) * 0.3
        time_penalty = max(-0.2, 1.0 - (event.response_time / 60000))
        
        event_reward = correctness + difficulty_bonus + time_penalty
        total_reward += event_reward
        node_rewards[node] = node_rewards.get(node, 0) + event_reward
        
        # Actualizar proficiencia del nodo
        if node not in updated_proficiency:
            updated_proficiency[node] = 0.0
        
        if correct:
            updated_proficiency[node] = min(1.0, updated_proficiency[node] + 0.05)
        else:
            updated_proficiency[node] = max(0.0, updated_proficiency[node] - 0.02)
    
    return {
        "total_reward": round(total_reward, 2),
        "node_rewards": {k: round(v, 2) for k, v in node_rewards.items()},
        "updated_proficiencies": {k: round(v, 3) for k, v in updated_proficiency.items()},
        "success_rate": round(
            sum(1 for e in events_data if e.correct) / len(events_data), 
            3
        ) if events_data else 0.0
    }


# ============= ENDPOINTS =============

def setup_endpoints(app):
    """
    Registra los endpoints en la app FastAPI
    """
    
    @app.post("/next-exercise")
    def next_exercise(request: NextExerciseRequest):
        """
        Recomienda el siguiente ejercicio basado en proficiencia del estudiante
        
        Con soporte opcional para focus nodes
        """
        try:
            model = get_model()
            state_dict = request.student_state.dict()
            
            focus_config = request.focus
            focus_nodes = focus_config.nodes if focus_config else None
            strict = focus_config.strict if focus_config else False
            
            recommendation = predict_with_focus(
                model,
                state_dict,
                focus_nodes=focus_nodes,
                strict=strict
            )
            
            return {
                "status": "success",
                "data": recommendation
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    @app.post("/session-end")
    def session_end(request: SessionEndRequest):
        """
        Calcula recompensa y proficiencia actualizada de una sesión
        
        NO persiste datos (eso lo hace otro backend)
        """
        try:
            result = calculate_session_reward(request.session_events)
            
            return {
                "status": "success",
                "data": result
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
