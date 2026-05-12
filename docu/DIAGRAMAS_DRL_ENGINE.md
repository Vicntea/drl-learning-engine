# 📊 Diagramas y Visualizaciones del Sistema DRL

## 1. Flujo de Recomendación de Ejercicios

```
┌─────────────────────────────────────────────────────────────┐
│                   ESTUDIANTE INICIA SESIÓN                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │      StudentState Actual             │
        ├──────────────────────────────────────┤
        │ knowledge:        {1a: 0.7, 2a: 0.3} │
        │ accuracy:         {1a: 0.85, 2a: 0.5}│
        │ attempts:         {1a: 15, 2a: 6}    │
        │ streak:           3                   │
        │ time_since_last:  2.5 hours          │
        └──────────────────────────────┬────────┘
                                      │
                    ┌─────────────────▼─────────────────┐
                    │  state_to_observation()           │
                    │  (Conversión a vector binario)    │
                    │  Umbral: proficiency >= 0.5       │
                    └────────────────┬──────────────────┘
                                     │
                  ┌──────────────────▼──────────────────┐
                  │   Observación para PPO              │
                  │   obs = [0, 1, 0, 1, 1, 0, ...]   │
                  │   Dimensión: 23 (num nodos)        │
                  └────────────────┬─────────────────────┘
                                   │
                   ┌───────────────▼────────────────┐
                   │   Modelo PPO.predict(obs)      │
                   │   policy("MlpPolicy")          │
                   └────────────────┬────────────────┘
                                    │
                   ┌────────────────▼─────────────────────┐
                   │   PPO Output                         │
                   │   action = 2 (índice de nodo)       │
                   │   _states = [estado interno RNN]    │
                   └────────────────┬─────────────────────┘
                                    │
                    ┌───────────────▼────────────────┐
                    │  idx_to_skill[int(action)]     │
                    │  selected_skill = "1a"         │
                    └────────────────┬────────────────┘
                                     │
        ┌────────────────────────────▼────────────────────────┐
        │  calculate_difficulty(skill_proficiency)           │
        ├─────────────────────────────────────────────────────┤
        │  proficiency = 0.7                                  │
        │  if proficiency < 0.3: difficulty = 1              │
        │  elif proficiency < 0.7: difficulty = 2            │
        │  else: difficulty = 3                              │
        │  ─────────────────────────────────────              │
        │  → difficulty = 3 (Avanzado)                        │
        └─────────────────┬──────────────────────────────────┘
                          │
        ┌─────────────────▼───────────────────────┐
        │  GENERATOR_MAP["1a"](difficulty=3)      │
        │  generate_1a_exercise(3)                │
        └─────────────────┬───────────────────────┘
                          │
        ┌─────────────────▼────────────────────────────────┐
        │         EJERCICIO GENERADO                       │
        ├──────────────────────────────────────────────────┤
        │ {                                                │
        │   "node": "1a",                                  │
        │   "type": "dictado",                            │
        │   "difficulty": 3,                              │
        │   "exercise": "Escucha y escribe...",          │
        │   "rhythm_pattern": ["q", "h", "8", "8"],      │
        │   "audio_source": "path/to/audio.mp3"          │
        │ }                                                │
        └─────────────────┬────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────────────┐
        │     SE PRESENTA AL ESTUDIANTE                │
        │     [Audio/Gráfico de ejercicio]             │
        └─────────────────┬───────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────────────┐
        │     ESTUDIANTE INTENTA RESOLVER             │
        │     [Input: respuesta del estudiante]        │
        └─────────────────┬───────────────────────────┘
                          │
                          ▼
        ┌──────────────────────────────────────────────────┐
        │  EVALUACIÓN Y CÁLCULO DE RECOMPENSA             │
        ├──────────────────────────────────────────────────┤
        │  correct = True                                  │
        │  response_time = 120 segundos                    │
        │  reward = calculate_reward(True, "1a", 3)       │
        │  ──────────────────────────────────────          │
        │  Componentes:                                    │
        │  - Base:                +1.0 (correcto)         │
        │  - Mejora:              +0.5 (progreso)         │
        │  - Dificultad óptima:   +0.5 (|diff-ideal| ≤ 1)│
        │  - Exploración:         +0.2 (¿primer intento?) │
        │  ─────────────────────────────────────           │
        │  Total reward:          ~2.2                     │
        └──────────────────┬───────────────────────────────┘
                           │
        ┌──────────────────▼─────────────────────────────┐
        │  ACTUALIZAR ESTADO DEL ESTUDIANTE              │
        ├──────────────────────────────────────────────────┤
        │  student.attempts["1a"] += 1          → 16       │
        │  student.accuracy["1a"] = (0.85*15 + 1)/16    │
        │                         → 0.859                 │
        │  student.knowledge["1a"] += 0.05      → 0.75   │
        │  student.streak += 1                  → 4       │
        │  student.recent_performance_trend["1a].append(1)│
        │  frustration_level -= 1               → (calmado)│
        └──────────────────┬──────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────────┐
        │     ESTADO ACTUALIZADO               │
        │     (Listo para siguiente ejercicio) │
        └──────────────────────────────────────┘
```

---

## 2. Estructura del Entorno de Aprendizaje (Gymnasium)

```
┌─────────────────────────────────────────────────────────┐
│         MusicLearningEnv (gymnasium.Env)                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  MÉTODOS PRINCIPALES:                                   │
│  ─────────────────────                                  │
│                                                          │
│  reset(initial_state=None)                             │
│  │                                                      │
│  ├─ Si initial_state es None:                          │
│  │   └─ Crear UserState por defecto                    │
│  │      ├─ knowledge[nodo] = 0.0                       │
│  │      ├─ accuracy[nodo] = 0.0                        │
│  │      ├─ attempts[nodo] = 0                          │
│  │      ├─ streak = 0                                  │
│  │      └─ recent_performance_trend = []               │
│  │                                                      │
│  ├─ current_step = 0                                    │
│  └─ return: (observation, info)                        │
│                                                          │
│  ───────────────────────────────────────────────────── │
│                                                          │
│  step(action, correct, response_time)                  │
│  │                                                      │
│  ├─ Validar action ∈ [0, len(exercise_catalog)]       │
│  │                                                      │
│  ├─ exercise = exercise_catalog[action]               │
│  │ └─ node = exercise.node                            │
│  │ └─ difficulty = exercise.difficulty                │
│  │ └─ prerequisites = exercise.prerequisites          │
│  │                                                      │
│  ├─ ENFORCEMENT DE PREREQUISITOS:                      │
│  │  if prerequisites:                                  │
│  │    for prerequisite in prerequisites:              │
│  │      if knowledge[prerequisite] <= 0.6:            │
│  │        return -1.0 reward  # ✗ NO PERMITIDO        │
│  │                                                      │
│  ├─ NO REPETIR EJERCICIOS:                            │
│  │  if exercise.id == last_exercise_id:               │
│  │    return -0.5 reward  # ⚠ PENALIZADO              │
│  │                                                      │
│  ├─ ACTUALIZAR INTENTOS:                              │
│  │  attempts[node] += 1                               │
│  │                                                      │
│  ├─ ACTUALIZAR ACCURACY:                              │
│  │  accuracy[node] = (acc_prev * (n-1) + correct) / n │
│  │                                                      │
│  ├─ ACTUALIZAR CONOCIMIENTO (si correcto):            │
│  │  if correct:                                        │
│  │    knowledge[node] = min(1.0,                       │
│  │      knowledge[node] + 0.05)                       │
│  │    streak += 1                                      │
│  │  else:                                              │
│  │    knowledge[node] = max(0.0,                       │
│  │      knowledge[node] - 0.02)                       │
│  │    streak = 0                                       │
│  │                                                      │
│  ├─ CALCULAR RECOMPENSA:                              │
│  │  reward = calculate_reward(correct, node, diff)    │
│  │  └─ (Desglose en siguiente diagrama)               │
│  │                                                      │
│  ├─ TERMINAR EPISODIO:                                │
│  │  done = current_step >= max_steps                  │
│  │      or all(knowledge[n] >= 0.95)                  │
│  │                                                      │
│  └─ return: (obs, reward, done, False, info)          │
│                                                          │
│  ───────────────────────────────────────────────────── │
│                                                          │
│  _get_obs()                                            │
│  └─ return UserState actual (no conversión a vector)  │
│                                                          │
│  render()                                              │
│  └─ Imprime estado actual (para debugging)             │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 3. Cálculo Detallado de Recompensa

```
┌─────────────────────────────────────────────────────────────┐
│              calculate_reward(correct, node, diff)          │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────▼──────────────┐
        │ ENTRADA (ejemplo)           │
        ├─────────────────────────────┤
        │ correct = True              │
        │ node = "1a"                 │
        │ difficulty = 3              │
        │                             │
        │ knowledge["1a"] = 0.7       │
        │ recent_performance_trend    │
        │   ["1a"] = [0, 1, 1, 1]    │
        │                             │
        │ attempts["1a"] = 8          │
        │                             │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼────────────────────────────┐
        │ 1️⃣  TENDENCIA RECIENTE                    │
        │                                           │
        │ trend = [0, 1, 1, 1]                      │
        │ prev = trend[-2:] = [1, 1]                │
        │ improvement = 1 - 1 = 0 (sin cambio)      │
        └──────────────┬────────────────────────────┘
                       │
        ┌──────────────▼────────────────────────────┐
        │ 2️⃣  DIFICULTAD IDEAL                      │
        │                                           │
        │ ideal_difficulty = int(0.7 * 10) = 7     │
        │ diff_gap = |3 - 7| = 4                    │
        │                                           │
        │ ⚠️  GAP > 2: Muy fácil, penalizar        │
        └──────────────┬────────────────────────────┘
                       │
        ┌──────────────▼────────────────────────────┐
        │ 3️⃣  FLAGS DE EXPLORACIÓN                  │
        │                                           │
        │ nodo_poco_practicado = 8 < 3 ? False     │
        │ ejercicio_nuevo = len(trend) <= 1 ? False│
        │                                           │
        │ No hay bonificación de exploración        │
        └──────────────┬────────────────────────────┘
                       │
        ┌──────────────▼────────────────────────────────────┐
        │ 4️⃣  CÁLCULO DE RECOMPENSA (Suma de componentes)  │
        │                                                   │
        │  reward = 1.0 * int(correct)       = 1.0         │
        │                                                   │
        │  if improvement (0 != 0?):          FALSE         │
        │    reward += 0.5                   → NO SE SUMA   │
        │                                                   │
        │  if diff_gap <= 1 (4 <= 1?):       FALSE         │
        │    reward += 0.5                   → NO SE SUMA   │
        │  elif diff_gap > 2 (4 > 2?):       TRUE          │
        │    reward -= 0.3                   → SE RESTA     │
        │    reward = 1.0 - 0.3 = 0.7                      │
        │                                                   │
        │  if nodo_poco_practicado:          FALSE         │
        │    reward += 0.2                   → NO SE SUMA   │
        │                                                   │
        │  if ejercicio_nuevo:               FALSE         │
        │    reward += 0.1                   → NO SE SUMA   │
        │                                                   │
        └──────────────┬───────────────────────────────────┘
                       │
        ┌──────────────▼───────────────────┐
        │ 5️⃣  RESULTADO                    │
        │                                  │
        │ 🔴 reward = 0.7 (Penalizado)   │
        │                                  │
        │ Interpretación:                  │
        │ ✓ Respuesta correcta             │
        │ ✗ Ejercicio muy fácil (gap=4)   │
        │ → No está escalando bien         │
        └──────────────────────────────────┘
```

### Casos de Ejemplo de Recompensa

```
┌─────────────────────────────────────────────────────────┐
│  CASO IDEAL: Correcta + Dificultad Óptima + Exploración│
├─────────────────────────────────────────────────────────┤
│                                                          │
│  correct = True, gap = 0, attempts = 2                 │
│                                                          │
│  Base:              +1.0                                │
│  Mejora (cambio):   +0.5                                │
│  Dificultad OK:     +0.5 (gap ≤ 1)                      │
│  Exploración:       +0.2 (< 3 intentos)                 │
│  ─────────────────────────                              │
│  TOTAL:             +2.2 🎉                             │
│                                                          │
│  → El agente aprendará a mantener esta dificultad      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  CASO MALO: Incorrecta                                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  correct = False                                        │
│                                                          │
│  Base:              +0.0                                │
│  (Resto no se suma)                                     │
│  ─────────────────                                      │
│  TOTAL:             0.0 ⛔                              │
│                                                          │
│  → Sin recompensa, pero tampoco castigo fuerte         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  CASO MODERADO: Correcta pero Dificultad Muy Alta       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  correct = True, gap = 5 (mucho salto)                 │
│                                                          │
│  Base:              +1.0                                │
│  Mejora:            +0.5                                │
│  Penalización:      -0.3 (gap > 2)                      │
│  ─────────────────────────                              │
│  TOTAL:             +1.2 📉                             │
│                                                          │
│  → Se desanima hacer saltos tan grandes                │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  CASO EXPLORACIÓN: Nodo Nuevo                           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  correct = True, ejercicio_nuevo = True                 │
│  dificultad óptima pero primer intento                 │
│                                                          │
│  Base:              +1.0                                │
│  Mejora:            +0.5                                │
│  Dificultad OK:     +0.5                                │
│  Variedad:          +0.1 (primer ejercicio)            │
│  ─────────────────────────────                          │
│  TOTAL:             +2.1 🌟                             │
│                                                          │
│  → Se bonifica exploración de nodos nuevos             │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Flujo de Datos: Trainer → Entorno → Agent

```
┌──────────────────────────────────────────────────────────────────┐
│                    SCRIPT: train_agent.py                         │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         │ 1. make_vec_env(create_env, n_envs=1)
                         │
        ┌────────────────▼────────────────┐
        │  VecEnv (1 entorno paralelo)    │
        │  ├─ step([action])              │
        │  ├─ reset()                     │
        │  └─ get_attr(), set_attr()      │
        └────────────────┬────────────────┘
                         │
                         │ 2. PPO(policy="MlpPolicy", env=vecenv)
                         │
        ┌────────────────▼──────────────────────────┐
        │         Modelo PPO                        │
        │  ┌────────────────────────────────────┐   │
        │  │  Actor (Política π)                │   │
        │  │  ├─ Input: obs (23 dims)           │   │
        │  │  ├─ Hidden: 64 → 64 neuronas      │   │
        │  │  └─ Output: μ, σ (acción)         │   │
        │  └────────────────────────────────────┘   │
        │  ┌────────────────────────────────────┐   │
        │  │  Critic (Función de valor V)       │   │
        │  │  ├─ Input: obs                     │   │
        │  │  ├─ Hidden: 64 → 64 neuronas      │   │
        │  │  └─ Output: V(s)                   │   │
        │  └────────────────────────────────────┘   │
        └────────────────┬──────────────────────────┘
                         │
                         │ 3. model.learn(total_timesteps=10000)
                         │
        ┌────────────────▼──────────────────────────────────┐
        │           LOOP DE ENTRENAMIENTO                   │
        │                                                    │
        │  for step in range(10000):                        │
        │    │                                              │
        │    ├─ obs, info = env.reset() [o continua]       │
        │    │                                              │
        │    ├─ obs = UserState (objeto)                   │
        │    │  └─ convertido internamente a vector        │
        │    │                                              │
        │    ├─ action = PPO.predict(obs)[0]               │
        │    │  └─ Acción determinista en entrenamiento    │
        │    │                                              │
        │    ├─ obs_next, reward, done, info = env.step()  │
        │    │                                              │
        │    ├─ Almacenar transición en buffer             │
        │    │  (observation, action, reward, V(s), etc)  │
        │    │                                              │
        │    ├─ Si buffer lleno o done:                    │
        │    │    │                                         │
        │    │    ├─ Calcular Ventaja: A = r + γV(s') - V(s)│
        │    │    │                                         │
        │    │    ├─ PPO Update:                           │
        │    │    │  ├─ Actor loss:  -A * log π(a|s)     │
        │    │    │  ├─ Critic loss: (V(s) - target)²     │
        │    │    │  └─ Entreropía: -β * H(π)             │
        │    │    │                                         │
        │    │    └─ optimizer.step()                      │
        │    │                                              │
        │    └─ Logging: reward, loss, etc.                │
        │                                                    │
        └────────────────┬──────────────────────────────────┘
                         │
                         │ 4. model.save(model_path)
                         │
        ┌────────────────▼──────────────────────┐
        │  Checkpoint Guardado                  │
        │  ppo_music_learning.zip               │
        │  ├─ model.pth                         │
        │  ├─ policy.pkl                        │
        │  └─ replay_buffer.pkl                 │
        └───────────────────────────────────────┘
```

---

## 5. Estructura del Árbol Curricular (Graph)

```
                        Nivel 1: FUNDAMENTOS
                        ┌────────────────────┐
                        │    1a: Ritmo       │
                        │   (Duración)       │
                        └────────────────────┘
                            │         │
                            ▼         ▼
                ┌──────────────┐  ┌──────────────┐
                │  1b: Notación│  │  1c: Compás  │
                └──────────────┘  └──────────────┘
                    │   │            │
                    └───┼────────────┘
                        ▼
                        Nivel 2: RECONOCIMIENTO
        ┌───────────────────────────────────────────┐
        │                                            │
    ┌──▼─────┐              ┌──▼─────┐        ┌──▼──────┐
    │ 2a:    │              │ 2b:    │        │ 2c:     │
    │Intervalos              │Escalas │        │Acordes  │
    └────────┘              └────────┘        └─────────┘
        │                       │                  │
        │                       │                  ▼
        │                       │          ┌──────────────┐
        │                       │          │ 2c-II: Inv. │
        │                       │          └──────────────┘
        └───────────┬───────────┘
                    ▼
                    Nivel 3: APLICACIÓN
        ┌───────────────────────────────────────────┐
        │                                            │
    ┌──▼─────┐              ┌──▼─────┐        ┌──▼──────┐
    │ 3a:    │              │ 3b:    │        │ 3c:     │
    │Progres. │              │Funcs.  │        │Modulación
    │Armonicas│              │Armonicas│       │         │
    └────────┘              └────────┘        └─────────┘


    RELACIONES (Prerequisitos):
    ─────────────────────────
    - 1a es prerequisito de: 1b, 2a, 2b
    - 1b es prerequisito de: 2c, 3a
    - 2a es prerequisito de: 2b
    - 2b es prerequisito de: 3a, 3b
    - 2c es prerequisito de: 3c
    - 3a, 3b son prerequisitos de: niveles 4+
```

---

## 6. Ciclo de Vida de una Sesión

```
INICIO DE SESIÓN (9 ejercicios)
│
├─ student.reset_session_tracking()
│  ├─ session_attempts = {nodo: 0, ...}
│  ├─ frustration_level -= 1
│  └─ consecutive_successes = {nodo: 0, ...}
│
├─ LOOP: for step in range(9):
│  │
│  ├─ step=0: [Ejercicio sobre 1a]
│  │  ├─ agent.predict(obs) → acción=0 ("1a")
│  │  ├─ generate_1a_exercise(difficulty=2)
│  │  ├─ estudiante responde → correcto=True
│  │  ├─ reward = 2.1 ✓
│  │  └─ state.update(1a, True)
│  │
│  ├─ step=1: [Ejercicio sobre 2a]
│  │  ├─ agent.predict(obs) → acción=3 ("2a")
│  │  ├─ generate_2a_exercise(difficulty=1)
│  │  ├─ estudiante responde → correcto=False
│  │  ├─ reward = 0.0 ✗
│  │  └─ state.update(2a, False)
│  │
│  ├─ step=2-7: [Más ejercicios...]
│  │
│  └─ step=8: [Ejercicio final]
│     ├─ agent.predict(obs) → acción=0 ("1a")
│     ├─ generate_1a_exercise(difficulty=3)
│     ├─ estudiante responde → correcto=True
│     ├─ reward = 2.2 ✓
│     └─ state.update(1a, True)
│
└─ FIN DE SESIÓN
   ├─ Guardar sesión en JSONL
   ├─ Calcular métricas de sesión
   └─ Siguiente sesión (si aplica)

    DATOS GUARDADOS EN JSONL:
    ─────────────────────────
    {
      "student_id": "sint_0100",
      "session_id": "sint_0100_ses_1",
      "session_events": [
        {
          "step": 0,
          "action": "1a",
          "outcome": {correct: true, score: 95, time: 120},
          "reward": 2.1,
          "state_before": {...}
        },
        ...
      ],
      "session_summary": {
        "total_reward": 14.3,
        "avg_accuracy": 0.777,
        "nodes_practiced": ["1a", "2a", "1b"],
        "avg_difficulty": 2.1
      }
    }
```

---

## 7. Componentes de Input/Output de Generador de Ejercicio

```
┌──────────────────────────────────────────────────────┐
│           Node Generator (ej: node_1a.py)            │
└──────────────────────────────────────────────────────┘

INPUT:
  ├─ difficulty: int [1, 2, 3]
  ├─ last_type: str (opcional) ["theory", "practice", "dictation"]
  └─ exercise_type: str (si se fuerza un tipo específico)

PROCESO (Internamente):
  │
  ├─ Si difficulty == 1:
  │  └─ Figuras simples: Negra, Blanca
  │
  ├─ Si difficulty == 2:
  │  └─ + Corcheas, Silencios
  │
  ├─ Si difficulty == 3:
  │  └─ + Semicorcheas, Fusas (más complejo)
  │
  ├─ Elegir tipo: theory | practice | dictation
  │  (aleatorio si no se especifica)
  │
  └─ Generar ejercicio específico

OUTPUT (JSON):
  {
    "node": "1a",
    "type": "theory" | "practice" | "dictation",
    "difficulty": 1 | 2 | 3,
    
    // Para theory
    "exercise": "¿Cuántos tiempos vale...?",
    "expected_answer": "1 tiempo(s)",
    
    // Para practice/dictation
    "rhythm_pattern": ["q", "h", "8", "8"],
    "rhythm_sequence": ["Negra", "Blanca", "Corchea", "Corchea"],
    
    // Para dictation
    "audio_source": "path/to/audio.mp3",
    
    // Para visualización
    "presentation": {
      "midiData": "base64_encoded_midi",
      "notes": [
        {"keys": ["c/4"], "duration": "q"},
        {"keys": ["c/4"], "duration": "h"},
        ...
      ],
      "rhythmPattern": ["q", "h", "8", "8"]
    }
  }
```

---

## 8. Estados de Aprendizaje y Transiciones

```
┌────────────────────────────────────────────────────────┐
│         Máquina de Estados: Progreso del Nodo         │
└────────────────────────────────────────────────────────┘

    ┌────────────┐
    │   NUEVO    │  knowledge[nodo] = 0.0
    │  (Gris)    │  attempts = 0
    └─────┬──────┘
          │
          │ [PPO recomienda este nodo]
          │
          ▼
    ┌──────────────┐
    │ EN_PROGRESO  │  0.0 < knowledge < 0.6
    │ (Amarillo)   │  attempts ≥ 1
    └─────┬────────┘
          │
          ├─ [Respuesta correcta] ──→ knowledge += 0.05
          │                            streak++
          │
          ├─ [Respuesta incorrecta] ─→ knowledge -= 0.02
          │                            streak = 0
          │
          └─ [Múltiples correctas] ──→
               
          ▼
    ┌──────────────┐
    │ DOMINADO     │  knowledge ≥ 0.8
    │ (Verde)      │  attempts ≥ 10
    └─────┬────────┘
          │
          ├─ [Respuesta incorrecta] ──→ knowledge -= 0.1
          │  (¿Regresión?)               └─ Si < 0.7: vuelve a EN_PROGRESO
          │
          └─ [PPO elige otros nodos] ──→ [Nodo descuidado]


SÍMBOLOS FRUSTRACIÓN:
─────────────────────
    [Rojo] = Nodo problemático (múltiples fallos consecutivos)
            frustration_level > 3
            → Bajar dificultad automáticamente
            → Ofrecer feedback adicional


TRANSICIONES ESPECIALES:
────────────────────────
    (En_progreso) + [10 intentos sin mejora] → Frustración
    
    Dominado + [Prerequisito no dominado] → Bloqueo
    
    Nuevo + [Prerequisito no cumplido] → Salto rechazado (-1.0 reward)
```

---

## 9. Curva de Aprendizaje Esperada

```
Knowledge del Nodo
│
1.0 ├────────────────────────────┐
    │                            │ Mastery (0.95+)
0.95├─────────────┐              │
    │             │              │
0.80├─────────────┼──────┐       │
    │             │      │       │ Dominado (0.80+)
0.60├─────────────┼──────┼──┐    │
    │             │      │  │    │ Progreso (0.20-0.80)
0.40├──────┐      │      │  │    │
    │      │      │      │  │    │
0.20├──────┼──────┼──────┼──┼────┤
    │      │      │      │  │    │ Iniciado (>0.0)
0.00├──────┼──────┼──────┼──┼────┴──────────
    │ Nuevo│      │      │  │
    └──────────────────────────────────────── Tiempo (sesiones)
       ↑         ↑      ↑  ↑
       s0        s5     s10 s15  s20

FASES:
  Fase 1 (s0-s5):   Aprendizaje rápido inicial
                    - Primeros ejercicios
                    - Bonus de exploración
                    - Curva empinada

  Fase 2 (s5-s10):  Consolidación
                    - Conocimiento crece más lentamente
                    - Menos bonificaciones
                    - Dificultad aumenta

  Fase 3 (s10-s20): Dominio/Meseta
                    - Progreso mínimo
                    - Puede haber frustración
                    - Decide: mastery o cambio a otro nodo
```

---

## 10. Matriz de Decisión: Qué Hace El Agente

```
┌──────────────────────────────────────────────────────┐
│   PPO Observa Estado y Decide Acción                 │
└──────────────────────────────────────────────────────┘

ENTRADA (Observación Binaria):
  obs[0] = 1   → Nodo 1a dominado (≥0.5)
  obs[1] = 0   → Nodo 1b NO dominado
  obs[2] = 1   → Nodo 2a dominado
  obs[3] = 0   → Nodo 2b NO dominado
  obs[4] = 1   → Nodo 2c dominado
  ...
  obs[23] = 0  → Último nodo NO dominado

POLÍTICA APRENDIDA (Ejemplo después de entrenamiento):
  ─────────────────────────────────────────────────
  
  Observación Típica A:
    Student con: 1a, 1b, 2a dominados
    → PPO elige: Nodo 2b (prerequisito casi cumplido)
    → Dificultad: 1 (profundidad 0.3)
    → Incentiva progresar a 2b
  
  Observación Típica B:
    Student con: 1a dominado, todo lo demás débil
    → PPO elige: Nodo 1b (prerequisito necesario)
    → Dificultad: 2
    → Incentiva construir base sólida
  
  Observación Típica C:
    Student con: todos los nodos débiles
    → PPO elige: Nodo 1a (inicio)
    → Dificultad: 1
    → Comienza desde fundamentos


MATRIZ DE ACCIÓN → RECOMPENSA ESPERADA:
  ──────────────────────────────────────
  
  ┌─────────────────┬─────────────────┬──────────────────┐
  │    Acción       │   Escenario     │  Recompensa      │
  ├─────────────────┼─────────────────┼──────────────────┤
  │ Nodo débil      │ Prereq OK       │ +2.0 (explorar)  │
  │ (attempts < 3)  │ Dificultad OK   │                  │
  ├─────────────────┼─────────────────┼──────────────────┤
  │ Nodo débil      │ Prereq NO       │ -1.0 (bloqueo)   │
  │ (attempts < 3)  │                 │                  │
  ├─────────────────┼─────────────────┼──────────────────┤
  │ Nodo dominado   │ En óptimo       │ +1.2 (refuerzo)  │
  │ (attempts ≥ 10) │ (correcto)       │                  │
  ├─────────────────┼─────────────────┼──────────────────┤
  │ Nodo repetido   │ Mismo que antes │ -0.5 (penalizar)│
  │ (exercise_id)   │                 │ variedad        │
  ├─────────────────┼─────────────────┼──────────────────┤
  │ Nodo nuevo      │ 1er ejercicio    │ +0.1 (bonus)    │
  │ (1st attempt)   │ correcto        │ adicional       │
  └─────────────────┴─────────────────┴──────────────────┘


CONVERGENCIA ESPERADA:
  ──────────────────
  
  Después de ~10,000 timesteps:
  
  - PPO aprende a respetar prerequisitos ✓
  - PPO aprende a escalar dificultad gradualmente ✓
  - PPO aprende a explorar nodos débiles ✓
  - PPO aprende a evitar repetir ejercicios ✓
  - PPO aprende el balance exploración-explotación ✓
  
  Métrica clave: Curva de recompensa acumulada en 
                 entrenamiento (debe crecer)
```

