# 🎵 Análisis Completo: Sistema DRL para Enseñanza Musical Adaptativa

## 📋 Tabla de Contenidos
1. [Descripción General](#descripción-general)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Parámetros de Entrada](#parámetros-de-entrada)
4. [Entrenamiento del Modelo](#entrenamiento-del-modelo)
5. [Función de Recompensa](#función-de-recompensa)
6. [Sistema de Sesiones](#sistema-de-sesiones)
7. [Generación de Ejercicios](#generación-de-ejercicios)
8. [Flujo de Inferencia](#flujo-de-inferencia)
9. [Futuras Mejoras](#futuras-mejoras)

---

## Descripción General

El sistema `ia_drl_engine` es un motor de **Deep Reinforcement Learning (DRL)** basado en **PPO (Proximal Policy Optimization)** que:

- **Recomienda ejercicios musicales personalizados** según el estado del estudiante
- **Navega por un árbol de conceptos musicales** (grafo de prerequisitos)
- **Se adapta dinámicamente** a la curva de aprendizaje del alumno
- **Entrena con datos sintéticos** y se refina con datos reales

**Objetivo Principal**: Crear un **tutor musical inteligente y adaptativo** que optimice la enseñanza personalizada mediante retroalimentación continua.

---

## Arquitectura del Sistema

### 🏗️ Componentes Principales

```
ia_drl_engine/
├── src/
│   ├── env/
│   │   └── music_learning_env.py       # Entorno Gymnasium (RL)
│   ├── agents/
│   │   ├── inference.py                # Recomendaciones en producción
│   │   ├── load_agent.py               # Carga del modelo PPO
│   │   └── test_inference.py           # Tests de inferencia
│   ├── generators/
│   │   ├── base.py                     # Funciones base
│   │   └── nodes/
│   │       ├── node_1a.py              # Generador: Ritmo básico
│   │       ├── node_2a.py              # Generador: Intervalos
│   │       ├── node_2b.py              # Generador: Escalas
│   │       └── node_3a.py              # Generador: Acordes
│   ├── simulator/
│   │   └── data_generator.py           # Genera datos sintéticos
│   └── utils/
│       ├── skill_mapping.py            # Mapeo habilidades ↔ índices
│       ├── path_utils.py               # Utilidades de rutas
│       └── tree_visualizer.py          # Visualización de progreso
├── train_agent.py                      # Script: Entrenar PPO
├── train_bc.py                         # Script: Entrenar BC (Behavioral Cloning)
├── evaluate_agent.py                   # Script: Evaluar modelo
├── drl_inference.py                    # Singleton del modelo
├── main.py                             # FastAPI: API de inferencia
├── state_model.py                      # Modelo de estado del estudiante
└── exercise_schema.py                  # Esquema de ejercicios
```

### 📊 Flujo General

```
ESTUDIANTE
    ↓
[StudentState: proficiencias, accuracy, attempts, streak, etc.]
    ↓
state_to_observation() ← Conversión a vector 0/1
    ↓
[Modelo PPO]
    ↓
predict_next_exercise() ← Selecciona nodo + dificultad
    ↓
[Generador de Ejercicio] ← Crea ejercicio musical
    ↓
EJERCICIO GENERADO (teoría, práctica, dictado)
    ↓
[Estudiante resuelve]
    ↓
calculate_reward() ← Calcula recompensa
    ↓
update_state() ← Actualiza proficiencias
```

---

## Parámetros de Entrada

### 📥 Input: `StudentState`

Definido en `state_model.py`:

```python
@dataclass
class UserState:
    knowledge: Dict[str, float]              # Profundidad de conocimiento [0.0, 1.0]
    accuracy: Dict[str, float]               # Precisión en respuestas [0.0, 1.0]
    attempts: Dict[str, int]                 # Cantidad de intentos por habilidad
    streak: int                              # Racha de aciertos/fallos consecutivos
    last_exercise_difficulty: int            # Dificultad del último ejercicio (1-10)
    time_since_last_practice: float          # Horas desde última práctica
    recent_performance_trend: Dict[str, List[float]]  # Historial reciente de resultados
```

### 📊 Conversión a Observación

En `inference.py`:

```python
def state_to_observation(student_state):
    """
    Convierte StudentState a vector MultiBinary para PPO.
    
    Formato esperado por PPO: MultiBinary(23)
    - Cada dimensión = 1 si skill_proficiency >= 0.5, sino 0
    """
    obs = np.zeros(len(ordered_skills), dtype=np.int8)
    
    for skill, value in skill_proficiency.items():
        if skill in skill_to_idx and value >= 0.5:
            idx = skill_to_idx[skill]
            obs[idx] = 1  # Binaria: Dominado (1) vs No dominado (0)
    
    return obs
```

**Notas importantes:**
- El modelo PPO espera un **vector binario** de 23 dimensiones (número de nodos)
- Umbral: proficiencia ≥ 0.5 = "dominado" (1)
- Proficiencia < 0.5 = "no dominado" (0)

### 🎼 Nodos Disponibles

Mapeados en `skill_mapping.py` desde `@data/graph/nodes.json`:

```
1a → Ritmo básico (Duración y valor rítmico)
1b → Notación rítmica
2a → Intervalos
2b → Escalas mayores/menores
2c → Acordes básicos
3a → Progresiones armónicas
3b → Funciones armónicas
...
```

Ordenamiento: Por número (1-7) luego por letra (a-c)

---

## Entrenamiento del Modelo

### 🚀 Script de Entrenamiento: `train_agent.py`

```python
from stable_baselines3 import PPO
from gymnasium import spaces

# 1. Crear entorno
env = make_vec_env(create_env, n_envs=1)

# 2. Configurar modelo PPO
model = PPO(
    policy="MlpPolicy",           # Política: Red neuronal MLP
    env=env,
    verbose=1,
    tensorboard_log=tensorboard_path
)

# 3. Entrenar
TIMESTEPS = 10000
model.learn(total_timesteps=TIMESTEPS)

# 4. Guardar
model.save(model_path)
```

### 🎓 Entrenamiento con Behavioral Cloning: `train_bc.py`

**Alternativa**: Entrenamiento supervisado usando datos reales/sintéticos

```python
# Cargar datos JSONL o CSV
data = load_from_jsonl(dataset_path)

# Red neuronal: estado → acción
class BCModel(nn.Module):
    def __init__(self, input_size, num_skills):
        super().__init__()
        self.fc1 = nn.Linear(input_size, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, num_skills)
    
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.fc3(x)

# Entrenar con pérdida de entropía cruzada
optimizer = optim.Adam(model.parameters(), lr=1e-3)
criterion = nn.CrossEntropyLoss()

for epoch in range(epochs):
    for state, action in dataloader:
        pred = model(state)
        loss = criterion(pred, action)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
```

### 📊 Parámetros de Entrenamiento

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `TIMESTEPS` | 10,000 | Steps totales de entrenamiento |
| `n_envs` | 1 | Entornos paralelos (vectorizados) |
| `policy` | MlpPolicy | Red neuronal de política |
| `learning_rate` | 3e-4 (default PPO) | Tasa de aprendizaje |
| `gamma` | 0.99 (default) | Factor de descuento |
| `gae_lambda` | 0.95 (default) | GAE lambda |

### 📈 Datos de Entrenamiento: Estudiantes Sintéticos

Generados en `data_generator.py`:

```python
# Configuración
TOTAL_STUDENTS = 1500
MAX_STEPS_PER_STUDENT = 160
STEPS_PER_SESSION = 9

# Perfiles de estudiantes
profiles = [
    "desde_cero",    # Principiantes (33%)
    "parcial",       # Intermedios (33%)
    "avanzado"       # Avanzados (33%)
]

# Cada estudiante tiene:
# - skill_proficiency inicial según perfil
# - learning_rate aleatorio (±40% variación)
# - frustration_threshold personalizado
```

---

## Función de Recompensa

### 🎯 Cálculo de Recompensa

En `music_learning_env.py`, método `calculate_reward()`:

```python
def calculate_reward(self, correct, node, difficulty):
    """
    Componentes de recompensa (explora vs explota):
    
    1. **Recompensa base**: ±1.0 por correctitud
    2. **Mejora**: +0.5 si hay progreso en tendencia
    3. **Dificultad óptima**: +0.5 si |dificultad_ideal - dificultad| ≤ 1
    4. **Penalización**: -0.3 si salto muy grande (>2 niveles)
    5. **Exploración**: +0.2 si nodo poco practicado (<3 intentos)
    6. **Variedad**: +0.1 si ejercicio nuevo
    """
    
    # Obtener tendencia reciente
    trend = self.state.recent_performance_trend[node]
    prev = trend[-2:] if len(trend) > 1 else [0, 0]
    
    # ① Mejora detectada
    improvement = int(correct) - prev[-1] if prev else 0
    
    # ② Dificultad ideal vs actual
    ideal_difficulty = int(self.state.knowledge[node] * 10)
    diff_gap = abs(difficulty - ideal_difficulty)
    
    # ③ Bandera: nodo poco practicado
    nodo_poco_practicado = self.state.attempts[node] < 3
    
    # ④ Bandera: ejercicio nuevo
    ejercicio_nuevo = len(trend) <= 1
    
    # Calcular recompensa
    reward = 1.0 * int(correct)
    
    if improvement:
        reward += 0.5
    if diff_gap <= 1:
        reward += 0.5  # Explota zona óptima
    elif diff_gap > 2:
        reward -= 0.3  # Penaliza saltos grandes
    if nodo_poco_practicado:
        reward += 0.2  # Explora nodos débiles
    if ejercicio_nuevo:
        reward += 0.1  # Bonifica variedad
    
    return reward
```

### 📉 Desglose de Recompensas

**Caso 1: Respuesta CORRECTA + Dificultad Óptima + Nodo Débil**
```
Base:           +1.0
Mejora:         +0.5  (si hay progreso)
Dificultad OK:  +0.5  (gap ≤ 1)
Exploración:    +0.2  (< 3 intentos)
─────────────────────
Total:          ~2.2
```

**Caso 2: Respuesta INCORRECTA**
```
Base:           +0.0
Mejora:          0.0  (no hay progreso)
─────────────────────
Total:           0.0
```

**Caso 3: Respuesta CORRECTA + Dificultad muy alta (gap > 2)**
```
Base:           +1.0
Mejora:         +0.5
Penalización:   -0.3
─────────────────────
Total:          ~1.2
```

---

## Sistema de Sesiones

### 📝 Estructura de Sesiones

En `data_generator.py`:

```python
# Configuración
STEPS_PER_SESSION = 9  # Ejercicios por sesión

# Cada estudiante tiene:
# - Múltiples sesiones
# - Frustration_level decrece entre sesiones
# - Se reinician contadores de intentos por nodo
```

### 🔄 Ciclo de Sesión

```python
# Inicio de sesión
student.reset_session_tracking()
    ├─ Reset session_attempts[nodo] = 0
    ├─ frustration_level -= 1 (mejora ánimo)
    └─ consecutive_successes[nodo] = 0

# Dentro de sesión (repite 9 veces)
for step in range(STEPS_PER_SESSION):
    action = agent.predict(state)      # ← PPO elige nodo
    outcome = student.choose_action()  # ← Estudiante responde
    reward = calculate_reward(outcome) # ← Se calcula recompensa
    state = student.update_state(...)  # ← Se actualiza estado
    
# Fin de sesión
save_session_data()
```

### 📊 Datos de Sesión

Cada entrada en JSONL contiene:

```json
{
  "student_id": "sint_0100",
  "profile_type": "desde_cero",
  "step_number": 45,
  "session_id": "sint_0100_ses_1",
  "state": {
    "skill_proficiency": {
      "1a": 0.45,
      "1b": 0.20,
      "2a": 0.10,
      ...
    },
    "frustration_level": 2
  },
  "action": {
    "recommended_skill_id": "1a"
  },
  "outcome": {
    "success": true,
    "score": 95.5,
    "time_spent": 120
  },
  "reward": 1.8
}
```

---

## Generación de Ejercicios

### 🎼 Generador de Ejercicios: Node 1A (Ritmo)

En `node_1a.py`:

```python
# Constantes
FIGURES_BASIC = {
    "Negra": "q",      # Quarter: 1 beat
    "Blanca": "h",     # Half: 2 beats
    "Corchea": "8",    # Eighth: 0.5 beat
    "Silencio_N": "qr",# Rest: 1 beat
    "Redonda": "w"     # Whole: 4 beats
}

TIME_SIGNATURE = "4/4"  # 4 tiempos por compás
MAX_TIME = 4.0
```

### 📋 Tipos de Ejercicios

#### 1️⃣ **Teórico** (`_generate_1a_theory`)
```
Pregunta: "¿Cuántos tiempos vale la figura de Negra (q) en un compás de 4/4?"
Respuesta: "1 tiempo(s)"
```

#### 2️⃣ **Práctico** (`_generate_1a_practical`)
```
Patrón: Negra + Blanca + Corchea + Corchea
Tarea: "Reproduce este patrón rítmico"
Respuesta esperada: [1 beat, 2 beats, 0.5 beat, 0.5 beat]
```

#### 3️⃣ **Dictado** (`_generate_1a_dictation`)
```
Audio: [Secuencia rítmica]
Tarea: "Escucha y escribe las figuras musicales"
Respuesta esperada: ["q", "h", "8", "8"]
```

### 🎵 Dificultad Progresiva

```python
difficulty_levels = {
    1: [q, h],              # Solo negras y blancas
    2: [q, 8, qr],          # + Corcheas y silencios
    3: [q, 8, h, qr]        # Mezcla completa
}
```

### 🎯 Formato de Salida

```python
def generate_1a_exercise(difficulty: int, last_type: str = None):
    return {
        "node": "1a",
        "type": "theory|practice|dictation",  # Tipo aleatorio
        "difficulty": difficulty,              # 1-3
        "exercise": "Pregunta/tarea",
        "rhythm_pattern": ["q", "h", "8"],    # Si es práctica/dictado
        "audio_source": "path/to/audio.mp3",  # Si es dictado
        "expected_answer": pattern,
        "presentation_format": "text|rhythm_input|audio_input"
    }
```

---

## Flujo de Inferencia

### 🔍 Proceso de Recomendación

En `inference.py`:

```python
def predict_next_exercise(student_state):
    """
    Entrada: StudentState con proficiencias actuales
    Salida: Ejercicio recomendado con dificultad personalizada
    """
    
    # 1. Cargar modelo
    model = get_model()
    
    # 2. Convertir estado a observación binaria
    obs = state_to_observation(student_state)
    #    obs = [0, 1, 0, 1, 1, 0, ...]  # 23 dimensiones
    
    # 3. PPO predice acción (índice de nodo)
    action, _ = model.predict(obs)
    #           └─ action = 3 (por ejemplo)
    
    # 4. Traducir índice a ID de nodo
    selected_skill = idx_to_skill[int(action)]
    #                            └─ "1a"
    
    # 5. Fallback si no existe generador
    if selected_skill not in GENERATOR_MAP:
        selected_skill = "1a"  # Default: Nodo 1a
    
    # 6. Calcular dificultad heurística
    proficiency = student_state["skill_proficiency"].get(selected_skill, 0)
    
    if proficiency < 0.3:
        difficulty = 1
    elif proficiency < 0.7:
        difficulty = 2
    else:
        difficulty = 3
    
    # 7. Generar ejercicio
    generator_function = GENERATOR_MAP[selected_skill]
    exercise = generator_function(difficulty=difficulty)
    
    # 8. Retornar recomendación
    return {
        "recommended_node": selected_skill,
        "difficulty": difficulty,
        "exercise": exercise
    }
```

### 🌐 API FastAPI: `main.py`

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class StudentState(BaseModel):
    skill_proficiency: dict[str, float]
    preferred_node: str | None = None
    difficulty: int | None = None
    free_navigation: bool = True

@app.post("/next-exercise")
def next_exercise(state: StudentState):
    recommendation = predict_next_exercise(state.dict())
    return recommendation
```

**Ejemplo de uso:**
```bash
curl -X POST "http://localhost:8000/next-exercise" \
  -H "Content-Type: application/json" \
  -d '{
    "skill_proficiency": {
      "1a": 0.7,
      "1b": 0.4,
      "2a": 0.1
    },
    "free_navigation": true
  }'
```

---

## Evaluación del Modelo

### 📊 Script de Evaluación: `evaluate_agent.py`

```python
from stable_baselines3 import PPO

# Cargar modelo entrenado
model = PPO.load(model_path)

# Evaluar en 10 episodios
EPISODES = 10

for episode in range(EPISODES):
    obs, info = env.reset()
    
    terminated = False
    total_reward = 0
    
    while not (terminated or truncated):
        # Predicción determinista (sin exploración)
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
    
    print(f"Episode {episode + 1} - Total Reward: {total_reward}")
```

**Métricas útiles:**
- Recompensa promedio por episodio
- Tasas de acierto en cada nodo
- Curva de aprendizaje
- Distribución de dificultades recomendadas

---

## Futuras Mejoras

### 🚀 Mejoras Sugeridas

#### 1. **Refinamiento de Función de Recompensa**
- [ ] Incluir `time_spent` (más corto = mejor)
- [ ] Considerar `frustration_level` dinámico
- [ ] Penalizar "stuck zones" (progreso estancado)
- [ ] Bonificar progresos en prereq dependencies

```python
# Mejora propuesta
def calculate_reward_v2(correct, node, difficulty, time_spent, frustration_level):
    reward = 1.0 * int(correct)
    
    # Penalizar tiempo excesivo
    time_penalty = 0.1 * max(0, (time_spent - 300) / 600)  # >5min es malo
    
    # Bonificar baja frustración
    frustration_bonus = 0.2 * (1.0 - frustration_level / 10.0)
    
    return reward - time_penalty + frustration_bonus
```

#### 2. **Exploración vs Explotación Adaptativa**
- [ ] Epsilon-decay: reducir exploración gradualmente
- [ ] UCB (Upper Confidence Bound) para nodos
- [ ] Thompson Sampling para mejor balance

#### 3. **Integración con Datos Reales**
- [ ] Fine-tune con datos piloto reales
- [ ] Transfer learning desde modelos sintéticos
- [ ] A/B testing entre políticas

#### 4. **Modelar Independencia de Estudiantes**
- [ ] Agregar embeddings de estudiante (edad, experiencia previa)
- [ ] Predicción de "time to mastery" por perfil
- [ ] Detección de "learning plateaus"

```python
# Propuesta: Estudiante embedding
class EnhancedEnv(MusicLearningEnv):
    def __init__(self, student_profile):
        super().__init__()
        self.student_embedding = self.encode_student(student_profile)
        # age, prior_music_exp, learning_style, etc.
    
    def _get_obs(self):
        base_obs = super()._get_obs()
        return np.concatenate([base_obs, self.student_embedding])
```

#### 5. **Prerequisitos Dinámicos**
- [ ] Permitir "saltos" si confianza es alta
- [ ] Detectar requisitos que no necesitan mastery
- [ ] Caminos alternativos para diferentes estilos

#### 6. **Feedback Inmediato Mejorado**
- [ ] Explicaciones personalizadas por nodo
- [ ] Recomendaciones de "restudy" automáticas
- [ ] Audio/visual feedback in real-time

#### 7. **Múltiples Agentes (Multi-Agent RL)**
- [ ] Un agente por "estilo de enseñanza"
- [ ] Competencia entre políticas
- [ ] Meta-learning: elegir mejor agente para cada estudiante

```python
# Propuesta: Multi-agent selector
class MultiAgentSelector:
    def __init__(self):
        self.agents = {
            "aggressive": PPO.load("models/ppo_aggressive.zip"),
            "conservative": PPO.load("models/ppo_conservative.zip"),
            "balanced": PPO.load("models/ppo_balanced.zip")
        }
    
    def predict(self, student_state):
        # Elegir agente según histórico
        style = self.select_style(student_state)
        agent = self.agents[style]
        return agent.predict(obs)
```

#### 8. **Desempeño Escalable**
- [ ] Vectorizar entornos (n_envs > 1)
- [ ] Paralelizar generación de datos sintéticos
- [ ] Distributed training en GPU

#### 9. **Interpretabilidad y Explicabilidad**
- [ ] Visualizar decisiones del PPO (attention maps)
- [ ] SHAP values para explicar cada recomendación
- [ ] Audit trail de decisiones del agente

#### 10. **Validación Cruzada con Humanos**
- [ ] Estudios piloto con profesores
- [ ] Comparar PPO vs heurísticas tradicionales
- [ ] Métricas: student satisfaction, learning gain, retention

---

## 📚 Resumen Ejecutivo

| Aspecto | Detalle |
|--------|---------|
| **Modelo RL** | PPO (Proximal Policy Optimization) |
| **Observación** | Vector binario de 23 nodos (proficiencia ≥ 0.5) |
| **Acción** | Índice de nodo (0-22) |
| **Recompensa** | Multi-componente: corrección, mejora, dificultad, exploración |
| **Datos** | 1,500 estudiantes sintéticos × 160 pasos = ~240K transiciones |
| **Entrenamiento** | 10,000 timesteps en entorno vectorizado |
| **Inferencia** | API FastAPI que recibe StudentState y retorna Ejercicio |
| **Sesiones** | 9 ejercicios por sesión, frustración decrece entre sesiones |
| **Generadores** | 4+ tipos de ejercicios (ritmo, teoría, práctica, dictado) |

---

## 🔗 Archivos Clave

- **Entrenamiento**: `train_agent.py` + `train_bc.py`
- **Entorno**: `src/env/music_learning_env.py`
- **Inferencia**: `src/agents/inference.py` + `main.py`
- **Datos**: `src/simulator/data_generator.py`
- **Generadores**: `src/generators/nodes/node_*.py`
- **Evaluación**: `evaluate_agent.py`

