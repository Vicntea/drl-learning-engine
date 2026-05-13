# 🔧 Guía Práctica: Cómo Usar el DRL Engine

## 1. Instalación y Setup

### 📦 Instalación de Dependencias

```bash
# En la carpeta del proyecto
cd drl-learning-engine

# Crear entorno virtual (recomendado)
python -m venv env
source env/Scripts/activate  # Windows

# Instalar dependencias
pip install -r ia_drl_engine/requirements.txt

# Dependencias adicionales si necesitas entrenar BC
pip install torch  # Recomendado instalar desde pytorch.org
```

### 🔑 Variables de Entorno

Crear archivo `_envFiles/config.env`:

```env
# Configuración de rutas
MODEL_PATH=@models/ppo_music_learning.zip
DATA_PATH=@data/synthetic/synthetic_data.jsonl
GRAPH_PATH=@data/graph/nodes.json

# API
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO
```

---

## 2. Generar Datos Sintéticos de Entrenamiento

### Ejecutar Generador de Datos

```bash
cd ia_drl_engine

# Generar 1,500 estudiantes sintéticos
python src/simulator/data_generator.py

# Output: data/synthetic/synthetic_data.jsonl (~50MB)
# Contiene: 1,500 estudiantes × ~160 pasos = ~240K transiciones
```

### Inspeccionar Datos Generados

```python
import json

# Leer algunas líneas del JSONL
with open('data/synthetic/synthetic_data.jsonl') as f:
    for i, line in enumerate(f):
        if i >= 3:  # Primeras 3
            break
        record = json.loads(line)
        print(f"\nEstudiante: {record['student_id']}")
        print(f"Paso: {record['step_number']}")
        print(f"Nodo recomendado: {record['action']['recommended_skill_id']}")
        print(f"Proficiencias: {record['state']['skill_proficiency']}")
        print(f"Resultado: {record['outcome']}")
        print(f"Recompensa: {record['reward']}")
```

---

## 3. Entrenar el Modelo PPO

### Script Básico

```python
# ia_drl_engine/train_agent.py
# Ya incluido en el repo

python train_agent.py

# Output:
# Timestep 1000/10000
# Timestep 2000/10000
# ...
# Modelo guardado en: models/ppo_music_learning.zip
```

### Entrenar con Parámetros Personalizados

```python
from stable_baselines3 import PPO
from ia_drl_engine.src.env.music_learning_env import MusicLearningEnv
from stable_baselines3.common.env_util import make_vec_env

# Crear entorno personalizado
def create_env():
    return MusicLearningEnv(
        nodes_path="data/graph/nodes.json",
        max_steps=100,  # Aumentar para más exploración
        exercise_catalog=load_catalog()
    )

# Crear entornos vectorizados (paralelos)
env = make_vec_env(create_env, n_envs=4)  # 4 entornos en paralelo

# Modelo con hiperparámetros personalizados
model = PPO(
    policy="MlpPolicy",
    env=env,
    learning_rate=3e-4,
    n_steps=2048,         # Pasos antes de actualizar
    batch_size=64,
    n_epochs=10,          # Épocas de entrenamiento
    gamma=0.99,           # Factor de descuento
    gae_lambda=0.95,      # GAE lambda
    clip_range=0.2,       # PPO clip parameter
    ent_coef=0.01,        # Coeficiente de entropía
    verbose=1,
    tensorboard_log="tensorboard/"
)

# Entrenar
model.learn(total_timesteps=50000)  # Más timesteps

# Guardar
model.save("models/ppo_music_learning_v2")

print("✓ Modelo entrenado y guardado")
```

### Monitorizar Entrenamiento con TensorBoard

```bash
# En terminal paralela
tensorboard --logdir tensorboard/

# Visitar: http://localhost:6006
# Ver gráficas de:
# - Episode reward
# - Episode length
# - Loss del actor y crítico
```

---

## 4. Entrenar Modelo de Behavioral Cloning (Supervisado)

### Script de BC

```python
# ia_drl_engine/train_bc.py
# Existe en el repo

python train_bc.py \
    --dataset @data/synthetic/synthetic_data.jsonl \
    --model-out @models/bc_model.pth \
    --epochs 50 \
    --batch-size 128 \
    --lr 1e-3
```

### Comparar PPO vs BC

```python
import torch
from stable_baselines3 import PPO

# Cargar modelo PPO
ppo_model = PPO.load("models/ppo_music_learning.zip")

# Cargar modelo BC
bc_model = torch.load("models/bc_model.pth")

# Evaluar en el mismo test set
test_states = [...]  # 100 estados aleatorios

# PPO
ppo_correct = 0
for state in test_states:
    action_ppo, _ = ppo_model.predict(state)
    if action_ppo == ground_truth_action:
        ppo_correct += 1

# BC
bc_correct = 0
with torch.no_grad():
    for state in test_states:
        output = bc_model(torch.tensor(state, dtype=torch.float32))
        action_bc = output.argmax()
        if action_bc == ground_truth_action:
            bc_correct += 1

print(f"PPO Accuracy: {ppo_correct / len(test_states):.2%}")
print(f"BC Accuracy: {bc_correct / len(test_states):.2%}")
```

---

## 5. Usar el API para Recomendaciones

### Iniciar Servidor FastAPI

```bash
cd ia_drl_engine

# Opción 1: Uvicorn directo
uvicorn main:app --reload --port 8000

# Opción 2: Gunicorn (producción)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --port 8000
```

### Consumir API desde Python

```python
import requests
import json

# URL del servidor
BASE_URL = "http://localhost:8000"

# Estado inicial del estudiante
student_state = {
    "skill_proficiency": {
        "1a": 0.5,
        "1b": 0.3,
        "2a": 0.1,
        "2b": 0.0,
        "2c": 0.0,
        "3a": 0.0,
        "3b": 0.0,
        "3c": 0.0,
    },
    "preferred_node": None,
    "difficulty": None,
    "free_navigation": True
}

# Hacer request
response = requests.post(
    f"{BASE_URL}/next-exercise",
    json=student_state,
    headers={"Content-Type": "application/json"}
)

# Resultado
if response.status_code == 200:
    recommendation = response.json()
    print("Recomendación recibida:")
    print(json.dumps(recommendation, indent=2))
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

### Ejemplo de Respuesta

```json
{
  "recommended_node": "1a",
  "difficulty": 2,
  "exercise": {
    "node": "1a",
    "type": "practice",
    "difficulty": 2,
    "exercise": "Reproduce este patrón rítmico en 4/4",
    "rhythm_pattern": ["q", "h", "8", "8"],
    "presentation": {
      "midiData": "TUhlABoAAAIAAAAFAA8B...",
      "notes": [
        {"keys": ["c/4"], "duration": "q"},
        {"keys": ["c/4"], "duration": "h"},
        {"keys": ["c/4"], "duration": "8"},
        {"keys": ["c/4"], "duration": "8"}
      ],
      "rhythmPattern": ["Negra", "Blanca", "Corchea", "Corchea"]
    }
  }
}
```

### Consumir desde cURL

```bash
# Test del endpoint
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

## 6. Integración Frontend

### Cliente TypeScript (music-exercises-module)

```typescript
// src/services/drl/drlClient.ts

import axios from 'axios';

interface StudentState {
  skill_proficiency: Record<string, number>;
  preferred_node?: string;
  difficulty?: number;
  free_navigation?: boolean;
}

interface Exercise {
  node: string;
  type: 'theory' | 'practice' | 'dictation';
  difficulty: number;
  exercise: string;
  presentation?: {
    midiData?: string;
    notes?: any[];
  };
}

interface Recommendation {
  recommended_node: string;
  difficulty: number;
  exercise: Exercise;
}

export async function getRecommendation(
  state: StudentState
): Promise<Recommendation> {
  const response = await axios.post<Recommendation>(
    'http://localhost:8000/next-exercise',
    state
  );
  return response.data;
}

export async function submitAnswer(
  exerciseId: string,
  answer: any,
  correct: boolean,
  responseTime: number
): Promise<{reward: number; feedback: string}> {
  // Implementar endpoint para feedback
  return {
    reward: correct ? 1.0 : 0.0,
    feedback: correct ? 'Correcto!' : 'Intenta de nuevo'
  };
}

// Uso en componente React
import { useState, useEffect } from 'react';

export function ExercisePlayer() {
  const [exercise, setExercise] = useState<Exercise | null>(null);
  const [studentState, setStudentState] = useState<StudentState>({
    skill_proficiency: {
      '1a': 0.5,
      '1b': 0.3,
      '2a': 0.1
    }
  });

  useEffect(() => {
    const loadExercise = async () => {
      const recommendation = await getRecommendation(studentState);
      setExercise(recommendation.exercise);
    };
    
    loadExercise();
  }, [studentState]);

  const handleSubmit = async (answer: any) => {
    const isCorrect = validateAnswer(answer, exercise!);
    const feedback = await submitAnswer(
      exercise!.node,
      answer,
      isCorrect,
      responseTime
    );
    
    // Actualizar estado
    setStudentState({
      ...studentState,
      skill_proficiency: {
        ...studentState.skill_proficiency,
        [exercise!.node]: studentState.skill_proficiency[exercise!.node] + 
                         (isCorrect ? 0.05 : -0.02)
      }
    });
  };

  return (
    <div>
      {exercise && (
        <>
          <h2>Ejercicio: {exercise.node}</h2>
          <p>Dificultad: {exercise.difficulty}</p>
          <div>{exercise.exercise}</div>
          <button onClick={() => handleSubmit(/*answer*/)}>
            Enviar respuesta
          </button>
        </>
      )}
    </div>
  );
}
```

---

## 7. Evaluar Modelo Entrenado

### Evaluación Completa

```bash
cd ia_drl_engine

# Ejecutar evaluación
python evaluate_agent.py

# Output:
# Episode 1 - Total Reward: 15.3
# Episode 2 - Total Reward: 14.8
# Episode 3 - Total Reward: 16.1
# ...
# Evaluación completada.
```

### Evaluación Manual Detallada

```python
from stable_baselines3 import PPO
from ia_drl_engine.src.env.music_learning_env import MusicLearningEnv

# Cargar modelo
model = PPO.load("models/ppo_music_learning.zip")

# Crear entorno
env = MusicLearningEnv(nodes_path="data/graph/nodes.json")

# Evaluar
n_episodes = 50
episode_rewards = []
episode_lengths = []

for episode in range(n_episodes):
    obs, info = env.reset()
    episode_reward = 0
    episode_length = 0
    done = False
    
    while not done:
        # Predicción determinista (sin exploración)
        action, _ = model.predict(obs, deterministic=True)
        
        # Simular respuesta del estudiante (aleatorio para demo)
        import random
        correct = random.random() < 0.5
        response_time = random.randint(60, 300)
        
        obs, reward, done, truncated, info = env.step(
            action,
            correct=correct,
            response_time=response_time
        )
        
        episode_reward += reward
        episode_length += 1
        done = done or truncated
    
    episode_rewards.append(episode_reward)
    episode_lengths.append(episode_length)
    
    print(f"Episode {episode+1}: Reward={episode_reward:.2f}, Steps={episode_length}")

# Estadísticas
import numpy as np
print(f"\nMedias:")
print(f"  Reward promedio: {np.mean(episode_rewards):.2f}")
print(f"  Reward std: {np.std(episode_rewards):.2f}")
print(f"  Longitud promedio: {np.mean(episode_lengths):.1f}")
print(f"  Max reward: {np.max(episode_rewards):.2f}")
print(f"  Min reward: {np.min(episode_rewards):.2f}")
```

---

## 8. Visualizar Progreso de Estudiante

### Generar Visualizaciones

```bash
cd ia_drl_engine

# Visualizar árbol de progreso de un estudiante
python -c "
from src.utils.tree_visualizer import load_musical_tree, process_student_sessions

all_nodes = load_musical_tree('data/graph/nodes.json')
process_student_sessions(
    'data/synthetic/synthetic_data.jsonl',
    'sint_0500',  # ID del estudiante
    all_nodes,
    'data/synthetic/learning_progress/'
)

print('✓ Gráficas generadas en data/synthetic/learning_progress/')
"
```

### Análisis en Jupyter

```python
# ia_drl_engine/notebooks/student_progress.ipynb

import json
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx

# Cargar datos
with open('../data/graph/nodes.json') as f:
    graph_data = json.load(f)

with open('../data/synthetic/synthetic_data.jsonl') as f:
    records = [json.loads(line) for line in f if 'sint_0100' in line]

# Convertir a DataFrame
df = pd.DataFrame(records)

# Visualizar progreso de conocimiento
skill_proficiency_history = []
for record in records:
    for skill, prof in record['state']['skill_proficiency'].items():
        skill_proficiency_history.append({
            'step': record['step_number'],
            'skill': skill,
            'proficiency': prof
        })

df_skills = pd.DataFrame(skill_proficiency_history)

# Gráfico
fig, ax = plt.subplots(figsize=(12, 6))
for skill in df_skills['skill'].unique():
    data = df_skills[df_skills['skill'] == skill]
    ax.plot(data['step'], data['proficiency'], label=skill, marker='o')

ax.set_xlabel('Pasos')
ax.set_ylabel('Profundidad de Conocimiento')
ax.set_title('Progreso del Estudiante sint_0100')
ax.legend()
plt.tight_layout()
plt.savefig('student_progress.png', dpi=150)
plt.show()

print("✓ Gráfica guardada: student_progress.png")
```

---

## 9. Debugging y Troubleshooting

### Problema: Modelo no entrena (reward = 0 siempre)

```python
# ✓ Verificar entorno
from ia_drl_engine.src.env.music_learning_env import MusicLearningEnv

env = MusicLearningEnv(nodes_path="data/graph/nodes.json")
obs, info = env.reset()

# Test manual de step
obs, reward, done, truncated, info = env.step(
    action=0,
    correct=True,      # Forzar correcto
    response_time=100
)

print(f"Reward: {reward}")  # Debe ser > 1.0

if reward < 1.0:
    print("❌ Error: calculate_reward() está retornando 0")
    # Revisar music_learning_env.py::calculate_reward()
```

### Problema: Estado observable vacío

```python
# Verificar conversión estado → observación
from ia_drl_engine.src.agents.inference import state_to_observation
from ia_drl_engine.src.utils.skill_mapping import load_skill_mapping

skill_to_idx, idx_to_skill, ordered_skills = load_skill_mapping()

test_state = {
    "skill_proficiency": {
        "1a": 0.7,  # Dominado
        "1b": 0.3,  # No dominado (< 0.5)
        "2a": 0.8,  # Dominado
    }
}

obs = state_to_observation(test_state)
print(f"Observación: {obs}")
# Debe tener algunos 1s (habilidades dominadas)

if sum(obs) == 0:
    print("❌ Todas las habilidades abajo del umbral")
    # Incrementar proficiencias de prueba
```

### Problema: API retorna error 500

```python
# Verificar carga del modelo
from ia_drl_engine.src.agents.load_agent import get_model

try:
    model = get_model()
    print("✓ Modelo cargado exitosamente")
except Exception as e:
    print(f"❌ Error cargando modelo: {e}")
    # Asegurarse de que models/ppo_music_learning.zip existe
    import os
    print(f"Archivos en models/:")
    for f in os.listdir("models"):
        print(f"  - {f}")
```

### Problema: Memoria agotada durante entrenamiento

```python
# Reducir parámetros de entrenamiento
model = PPO(
    policy="MlpPolicy",
    env=env,
    n_steps=512,        # ↓ Reducir (default: 2048)
    batch_size=32,      # ↓ Reducir (default: 64)
    n_epochs=5,         # ↓ Reducir (default: 10)
    learning_rate=1e-4, # ↓ Bajar learning rate
    verbose=1
)

# O usar entornos no vectorizados
env = MusicLearningEnv(nodes_path="data/graph/nodes.json")
model = PPO(policy="MlpPolicy", env=env)  # Sin make_vec_env
```

---

## 10. Casos de Uso Avanzados

### A. Fine-tuning con Datos Reales

```python
from stable_baselines3 import PPO

# Cargar modelo preentrenado (sintético)
model = PPO.load("models/ppo_music_learning.zip")

# Crear entorno con datos piloto reales
env_real = MusicLearningEnv(
    nodes_path="data/graph/nodes.json",
    data_source="data/pilot/real_student_data.jsonl"  # ← Datos reales
)

# Fine-tune (menos pasos)
model.learn(
    total_timesteps=5000,
    reset_num_timesteps=False  # Continuar desde timestep anterior
)

# Guardar modelo mejorado
model.save("models/ppo_music_learning_finetuned")
```

### B. Seleccionar Política Según Perfil del Estudiante

```python
class AdaptiveRecommender:
    def __init__(self):
        self.models = {
            "conservative": PPO.load("models/ppo_conservative.zip"),
            "balanced": PPO.load("models/ppo_balanced.zip"),
            "aggressive": PPO.load("models/ppo_aggressive.zip")
        }
    
    def select_policy(self, student_profile):
        # Decidir qué modelo usar según perfil
        if student_profile['learning_speed'] < 0.3:
            return "conservative"  # Ritmo lento
        elif student_profile['learning_speed'] > 0.7:
            return "aggressive"    # Ritmo rápido
        else:
            return "balanced"      # Ritmo medio
    
    def recommend(self, state, student_profile):
        policy_name = self.select_policy(student_profile)
        model = self.models[policy_name]
        action, _ = model.predict(state_to_observation(state))
        return action, policy_name

# Uso
recommender = AdaptiveRecommender()
action, policy_used = recommender.recommend(
    student_state={...},
    student_profile={'learning_speed': 0.5}
)
print(f"Recomendación usando política: {policy_used}")
```

### C. Exportar Modelo para Producción

```python
# Exportar PPO a ONNX (compatible con navegadores)
from stable_baselines3.common.policies import MlpPolicy
import onnx

model = PPO.load("models/ppo_music_learning.zip")

# Usar stable-baselines3 + skl2onnx o convertir manualmente
# (Nota: conversión ONNX es compleja, considerar TensorFlow.js)

# Alternativa: Exportar a TensorFlow
import tensorflow as tf
from stable_baselines3 import PPO

# (Requiere setup especial)
```

### D. Métricas Personalizadas

```python
# Callback para monitorear métricas durante entrenamiento
from stable_baselines3.common.callbacks import BaseCallback

class CustomCallback(BaseCallback):
    def __init__(self):
        super().__init__()
        self.episode_rewards = []
        self.episode_lengths = []
    
    def _on_step(self) -> bool:
        # Al final de cada episode
        if "episode" in self.locals:
            ep_reward = self.locals["episode"]["r"]
            ep_len = self.locals["episode"]["l"]
            self.episode_rewards.append(ep_reward)
            self.episode_lengths.append(ep_len)
            
            if self.num_timesteps % 1000 == 0:
                avg_reward = sum(self.episode_rewards[-10:]) / 10
                print(f"Timestep {self.num_timesteps}: Avg Reward = {avg_reward:.2f}")
        
        return True

# Usar callback
model = PPO(policy="MlpPolicy", env=env)
callback = CustomCallback()
model.learn(total_timesteps=10000, callback=callback)
```

---

## 📚 Resumen de Comandos Comunes

```bash
# Generar datos
python src/simulator/data_generator.py

# Entrenar modelo PPO
python train_agent.py

# Entrenar modelo BC
python train_bc.py --epochs 50

# Evaluar modelo
python evaluate_agent.py

# Iniciar API
uvicorn main:app --reload

# Visualizar progreso
python -c "from src.utils import tree_visualizer; ..."

# Abrir TensorBoard
tensorboard --logdir tensorboard/
```

