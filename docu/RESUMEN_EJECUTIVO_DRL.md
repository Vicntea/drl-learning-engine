# 📊 Resumen Ejecutivo: DRL Music Learning Engine

## 🎯 Objetivo
Crear un **tutor musical adaptativo basado en Deep Reinforcement Learning (PPO)** que:
- Recomienda ejercicios musicales personalizados
- Se adapta al nivel y ritmo de cada estudiante
- Navega un árbol de conceptos con requisitos previos
- Optimiza la enseñanza mediante retroalimentación continua

---

## 🏗️ Arquitectura de Alto Nivel

```
ESTUDIANTE
    ↓
[Estado: proficiencias, accuracy, attempts, streak, frustración]
    ↓
[PPO Policy] → Elige nodo + dificultad
    ↓
[Generador de Ejercicio] → Crea ejercicio musical (teoría/práctica/dictado)
    ↓
[Estudiante resuelve]
    ↓
[Función de Recompensa] → Calcula reward multidimensional
    ↓
[Actualiza estado] → Incrementa proficiencia si acierta
```

---

## 🔑 Componentes Principales

### 1. **Modelo RL (PPO)**
- **Tipo**: Proximal Policy Optimization (on-policy)
- **Entrada**: Vector binario [0/1] × 23 nodos (proficiencia ≥ 0.5)
- **Salida**: Índice de nodo (0-22) a recomendar
- **Entrenamiento**: 10,000 timesteps con 1,500 estudiantes sintéticos

### 2. **Entorno (Gymnasium)**
Espacios:
- **Observación**: `Dict` con `UserState` (knowledge, accuracy, attempts, streak, etc.)
- **Acciones**: Discrete(23) - seleccionar nodo
- **Rewards**: -1.0 a +2.2 (multidimensional)

### 3. **Generadores de Ejercicios**
Por nodo:
- **1a**: Ritmo básico (figuras, compases 4/4)
- **2a**: Intervalos
- **2b**: Escalas
- **3a**: Acordes
- Tipos: Teoría, Práctica, Dictado

### 4. **Datos de Entrenamiento**
- 1,500 estudiantes sintéticos
- 3 perfiles: desde_cero, parcial, avanzado
- ~240K transiciones
- Formato: JSONL con (estado, acción, resultado, recompensa)

---

## ⚙️ Función de Recompensa (Multi-Componente)

```
Recompensa = Base + Mejora + Dificultad + Exploración + Variedad

donde:
  Base             = 1.0 si correcto, 0.0 si incorrecto
  Mejora           = +0.5 si hay progreso en tendencia
  Dificultad       = +0.5 si gap ≤ 1, -0.3 si gap > 2
  Exploración      = +0.2 si nodo poco practicado (<3 intentos)
  Variedad         = +0.1 si ejercicio nuevo
```

**Rango**: [-1.0, +2.2] (típicamente 0.0 a 2.1)

---

## 📊 Datos Clave

| Concepto | Valor |
|----------|-------|
| **Estudiantes sintéticos** | 1,500 |
| **Pasos por estudiante** | ~160 |
| **Total transiciones** | ~240,000 |
| **Nodos/Habilidades** | 23 |
| **Tipos ejercicios** | Teoría, Práctica, Dictado |
| **Dificultades** | 1-3 (progresivo) |
| **Timesteps entrenamiento** | 10,000 |
| **Entornos paralelos** | 1 (escalable a N) |

---

## 🎯 Parámetros de Entrada (StudentState)

```python
{
  "skill_proficiency": {
    "1a": 0.7,  # [0.0, 1.0] - Dominio del concepto
    "2a": 0.3,
    ...
  },
  "accuracy": {
    "1a": 0.85,  # Precisión promedio de respuestas
    ...
  },
  "attempts": {
    "1a": 15,   # Número de intentos
    ...
  },
  "streak": 3,              # Aciertos/fallos consecutivos
  "last_exercise_difficulty": 2,
  "time_since_last_practice": 2.5,  # horas
  "recent_performance_trend": {
    "1a": [0, 1, 1, 1, ...]  # Últimos 10 resultados
  }
}
```

---

## 📤 Output: Recomendación de Ejercicio

```json
{
  "recommended_node": "1a",
  "difficulty": 2,
  "exercise": {
    "node": "1a",
    "type": "practice",
    "exercise": "Reproduce este patrón rítmico...",
    "rhythm_pattern": ["q", "h", "8", "8"],
    "presentation": {
      "midiData": "base64_encoded_audio",
      "notes": [
        {"keys": ["c/4"], "duration": "q"},
        ...
      ]
    }
  }
}
```

---

## 🎓 Sistema de Sesiones

```
Sesión = 9 ejercicios
├─ Inicio: Reset frustration, session_attempts
├─ Ejercicio 1-9: Agent predice → Estudiante resuelve → Reward
└─ Fin: Datos guardados en JSONL

Entre sesiones:
  frustration_level -= 1 (mejora ánimo)
  streak = 0 (se reinicia)
```

---

## 🧠 Flujo de Entrenamiento (train_agent.py)

1. **Generar datos**: 1,500 estudiantes × 160 pasos = 240K transiciones
2. **Crear entorno**: MusicLearningEnv(nodes_path, max_steps=50)
3. **Vectorizar**: make_vec_env(n_envs=1)
4. **Instanciar PPO**: `PPO("MlpPolicy", env)`
5. **Entrenar**: `model.learn(total_timesteps=10000)`
6. **Guardar**: `model.save("models/ppo_music_learning.zip")`

---

## 🔄 Flujo de Inferencia (main.py - FastAPI)

1. **Cliente envía** StudentState con proficiencias actuales
2. **API recibe** POST /next-exercise
3. **state_to_observation()** convierte a vector binario
4. **PPO.predict()** elige nodo
5. **calculate_difficulty()** ajusta por profundidad
6. **Generador** crea ejercicio específico
7. **Retorna** Recomendación JSON

**Latencia**: ~50ms por recomendación

---

## 📈 Métricas de Desempeño

### Esperadas después de entrenamiento:

| Métrica | Valor |
|---------|-------|
| Reward promedio / episodio | 12-16 |
| Tasa de éxito en ejercicios | 65-75% |
| Respeto de prerequisitos | 100% |
| Evita repeticiones | 95%+ |
| Escalado de dificultad | Gradual (≤1 nivel/session) |

---

## 🔍 Tecnologías Utilizadas

| Componente | Librería | Versión |
|-----------|----------|---------|
| RL | stable-baselines3 | 2.0.1 |
| Entorno | gymnasium | 1.2.0 |
| Números | numpy | 1.24.3 |
| NN | torch | 2.0+ |
| API | FastAPI | +latest |
| Servidor | Uvicorn | +latest |

---

## 🚀 Cómo Usar

### Entrenamiento
```bash
cd ia_drl_engine
python src/simulator/data_generator.py  # Generar datos
python train_agent.py                    # Entrenar PPO
python evaluate_agent.py                 # Evaluar
```

### API
```bash
uvicorn main:app --reload --port 8000

# Test
curl -X POST "http://localhost:8000/next-exercise" \
  -H "Content-Type: application/json" \
  -d '{"skill_proficiency": {"1a": 0.7, "2a": 0.3}}'
```

### Integración Frontend
```typescript
const recommendation = await fetch('/next-exercise', {
  method: 'POST',
  body: JSON.stringify(studentState)
}).then(r => r.json());

// Mostrar ejercicio recomendado
renderExercise(recommendation.exercise);
```

---

## ✅ Fortalezas del Sistema

| Fortaleza | Detalle |
|-----------|---------|
| **Adaptativo** | Ajusta dificultad dinámicamente |
| **Requisitos** | Respeta prerequisitos automáticamente |
| **Variación** | Diversifica tipos de ejercicios |
| **Escalable** | Vectorización para múltiples estudiantes |
| **Evaluable** | Métricas claras (reward, proficiencia) |
| **Extensible** | Fácil agregar nuevos nodos/generadores |

---

## ⚠️ Limitaciones Actuales

| Limitación | Impacto |
|-----------|---------|
| Datos sintéticos | Puede no generalizar a estudiantes reales |
| Recompensa simplista | No considera aspectos motivacionales |
| Sin detección de frustración | No adapta cuando estudiante se frustra |
| Sin feedback adaptativo | Todos reciben mismo tipo feedback |
| Univector de observación | No captura heterogeneidad del estudiante |
| Batch size 1 | Baja eficiencia en paralelo |

---

## 🔮 Mejoras Recomendadas (Prioridad)

### 🔴 ALTA (Implementar próximo)
1. **Recompensa multi-temporal** - Considera progreso a largo plazo
2. **Detección de plateau** - Cambia estrategia si no hay progreso
3. **Epsilon-greedy adaptativo** - Exploración decreciente

### 🟡 MEDIA
4. **Transfer learning** - Fine-tune con datos reales
5. **Student embeddings** - Capturar perfil único
6. **A/B testing** - Comparar estrategias

### 🟢 BAJA
7. **SHAP explicabilidad** - Entender decisiones
8. **xAPI integration** - Conectar con LMS
9. **Multi-agent RL** - Competencia entre políticas

---

## 📁 Archivos Documentación

Este análisis se compone de:

1. **ANALISIS_DRL_ENGINE.md** (este) - Descripción general y arquitectura
2. **DIAGRAMAS_DRL_ENGINE.md** - Diagramas de flujo y máquinas de estado
3. **GUIA_PRACTICA_DRL.md** - Ejemplos de código y uso
4. **MEJORAS_FUTURAS_DRL.md** - Propuestas de optimizaciones

---

## 🔗 URLs Importantes

| Recurso | URL |
|---------|-----|
| API Docs | `http://localhost:8000/docs` |
| TensorBoard | `http://localhost:6006` |
| Datos Sintéticos | `data/synthetic/synthetic_data.jsonl` |
| Modelo | `models/ppo_music_learning.zip` |
| Grafo Curricular | `data/graph/nodes.json` |

---

## 📞 Contacto y Soporte

- **Duda sobre entrenamiento**: Ver `train_agent.py`
- **Duda sobre inferencia**: Ver `src/agents/inference.py`
- **Duda sobre entorno**: Ver `src/env/music_learning_env.py`
- **Duda sobre generadores**: Ver `src/generators/nodes/`

---

## 📝 Licencia

Este proyecto es parte de la tesis de **Vicente Alves** en la Universidad Austral de Chile.

---

**Fecha**: Mayo 2026  
**Versión**: 1.0  
**Estado**: ✅ Funcional y documentado

