# 🎼 Tabla Rápida: Referencia del DRL Music Learning Engine

## 📊 TABLA 1: Componentes del Sistema

| Componente | Función | Entrada | Salida | Archivo |
|-----------|---------|---------|--------|---------|
| **StudentState** | Modelar progreso del estudiante | - | Dict con proficiencias | `state_model.py` |
| **Observación** | Convertir estado a vector para PPO | StudentState | [0/1]^23 | `inference.py` |
| **PPO Model** | Red neuronal de política-valor | Observación | Acción (nodo) | `train_agent.py` |
| **MusicLearningEnv** | Entorno Gymnasium | Acción, corrección | Reward, nuevo estado | `music_learning_env.py` |
| **Generador 1a** | Crear ejercicio ritmo | Dificultad | Ejercicio JSON | `node_1a.py` |
| **Generador 2a** | Crear ejercicio intervalos | Dificultad | Ejercicio JSON | `node_2a.py` |
| **Función Recompensa** | Calcular reward | Resultado, contexto | Número real [-1, 2.2] | `calculate_reward()` |
| **Data Generator** | Simular estudiantes | Config | 1500 estudiantes JSONL | `data_generator.py` |
| **FastAPI** | Servir recomendaciones | StudentState POST | Recomendación JSON | `main.py` |

---

## 📥 TABLA 2: Parámetros de Entrada (StudentState)

| Parámetro | Tipo | Rango | Ejemplo | Significado |
|-----------|------|-------|---------|------------|
| `knowledge[nodo]` | float | [0.0, 1.0] | 0.7 | Profundidad de comprensión |
| `accuracy[nodo]` | float | [0.0, 1.0] | 0.85 | Precisión en respuestas |
| `attempts[nodo]` | int | [0, ∞) | 15 | Número de intentos |
| `streak` | int | [0, ∞) | 3 | Aciertos/fallos consecutivos |
| `difficulty` | int | [1, 3] | 2 | Última dificultad |
| `time_since_last` | float | [0, ∞) | 2.5 | Horas desde última práctica |
| `performance_trend[nodo]` | List[int] | 10 últimos | [0,1,1,1] | Historial reciente |
| `frustration_level` | int | [0, 5] | 2 | Nivel de frustración |

---

## 📤 TABLA 3: Parámetros de Salida (Recomendación)

| Campo | Tipo | Ejemplo | Descripción |
|-------|------|---------|------------|
| `recommended_node` | str | "1a" | Nodo a practicar |
| `difficulty` | int | 2 | Nivel de dificultad |
| `exercise.node` | str | "1a" | Tipo de nodo |
| `exercise.type` | str | "practice" | teoría/práctica/dictado |
| `exercise.exercise` | str | "Reproduce..." | Enunciado |
| `exercise.rhythm_pattern` | List[str] | ["q", "h"] | Patrón (si aplica) |
| `exercise.presentation.midiData` | str (b64) | "TUhlABoA..." | Audio MIDI codificado |
| `exercise.presentation.notes` | List[Dict] | [{"duration":"q"}] | Notas para visualizar |

---

## 🧠 TABLA 4: Parámetros de Entrenamiento (PPO)

| Hiperparámetro | Valor | Rango | Efectoal cambiar |
|---|---|---|---|
| `learning_rate` | 3e-4 | [1e-5, 1e-2] | ↑ = convergencia rápida, inestable |
| `n_steps` | 2048 | [512, 4096] | ↑ = menos updates, menos memoria |
| `batch_size` | 64 | [16, 256] | ↑ = updates estables, lento |
| `n_epochs` | 10 | [1, 20] | ↑ = más entrenamiento, overfitting |
| `gamma` | 0.99 | [0.95, 0.999] | ↑ = considera futuro, inestable |
| `gae_lambda` | 0.95 | [0.9, 0.99] | ↑ = menos sesgo, más varianza |
| `clip_range` | 0.2 | [0.1, 0.3] | ↑ = más actualización, inestable |
| `ent_coef` | 0.01 | [0, 0.1] | ↑ = más exploración, más reward |

---

## 💰 TABLA 5: Componentes de Recompensa

| Componente | Base | Condición | Bonus | Descripción |
|-----------|------|-----------|-------|------------|
| **Correctitud** | 1.0 | correct=True | - | Acierto |
| | 0.0 | correct=False | - | Fallo |
| **Mejora** | - | trend[-2:] ↑ | +0.5 | Progreso visible |
| **Dificultad** | - | gap ≤ 1 | +0.5 | Zona óptima |
| | - | gap > 2 | -0.3 | Salto muy grande |
| **Exploración** | - | attempts < 3 | +0.2 | Nodo débil |
| **Variedad** | - | 1er ejercicio | +0.1 | Cambio de tipo |
| | | | | |
| **RANGO TOTAL** | **[-1.0, +2.2]** | - | - | Típico: [0.0, 2.1] |

---

## 📈 TABLA 6: Estados de Progreso

| Estado | Rango Knowledge | Color | Características |
|--------|-----------------|-------|-----------------|
| **NUEVO** | 0.0 | Gris | Nunca intentado |
| **EN_PROGRESO** | 0.0-0.6 | Amarillo | Aprendiendo |
| **CASI_DOMINADO** | 0.6-0.8 | Naranja | Casi ahí |
| **DOMINADO** | 0.8-0.95 | Verde | Listo para avanzar |
| **MAESTRÍA** | 0.95-1.0 | Verde oscuro | Completamente dominado |
| **FRUSTRADO** | (cualquiera) | Rojo | frustration_level ≥ 3 |

---

## 🎓 TABLA 7: Perfiles de Estudiante Sintético

| Perfil | % Estudiantes | Nodos Iniciales | Profundidad | Learning Rate |
|--------|---------------|-----------------|-------------|---|
| **desde_cero** | 33% | Nivel 1-2 | 0.1-0.35 | Base × [0.9-1.4] |
| **parcial** | 33% | Nivel 3-4 | 0.5-0.8 | Base × [0.9-1.4] |
| **avanzado** | 33% | Nivel 5-7 | 0.6-0.9 | Base × [0.9-1.4] |

---

## 🎼 TABLA 8: Nodos del Árbol Curricular

| ID | Nombre | Nivel | Prerrequisitos | Descripción |
|----|--------|-------|-----------------|------------|
| 1a | Ritmo básico | 1 | - | Duración de figuras (4/4) |
| 1b | Notación | 1 | 1a | Compases y silencios |
| 1c | Compás | 1 | 1b | Patrones de tiempo |
| 2a | Intervalos | 2 | 1a | Distancia entre notas |
| 2b | Escalas | 2 | 2a | Mayor/menor |
| 2c | Acordes | 2 | 2b | Triadas |
| 3a | Prog. Armónicas | 3 | 2b, 2c | IV-V-I |
| 3b | Func. Armónicas | 3 | 2c | Tónica, dominante |
| 3c | Modulación | 3 | 3a, 3b | Cambios de tonalidad |

---

## ⚙️ TABLA 9: Configuración de Sesión

| Parámetro | Valor | Mutable | Efecto |
|-----------|-------|---------|--------|
| `STEPS_PER_SESSION` | 9 | No | Ejercicios por sesión |
| `MAX_STEPS_PER_STUDENT` | 160 | Sí | Total de pasos en tesis |
| `MASTERY_THRESHOLD` | 0.75 | Sí | Profundidad para dominio |
| `MAX_SIMULATION_MASTERY` | 0.6 | Sí | Máximo nodos dominados |
| `max_steps_per_episode` | 50 | Sí | Pasos máximo en entorno |

---

## 📊 TABLA 10: Datos de Entrenamiento

| Métrica | Valor | Descripción |
|---------|-------|------------|
| **Estudiantes sintéticos** | 1,500 | Individuos únicos simulados |
| **Pasos por estudiante** | ~160 | Media de transiciones |
| **Total transiciones** | ~240,000 | Para entrenar PPO |
| **Timesteps PPO** | 10,000 | Actualizaciones de política |
| **Entornos paralelos** | 1 | Vectorización (escalable) |
| **Tamaño JSONL** | ~50 MB | Comprimido con gzip |
| **Nodos únicos** | 23 | Total de habilidades |
| **Tipos ejercicios** | 3 | Teoría, práctica, dictado |
| **Dificultades** | 3 | Niveles 1-3 |

---

## 🔍 TABLA 11: Errores Comunes y Soluciones

| Error | Causa | Solución |
|-------|-------|----------|
| Reward siempre 0 | calculate_reward no se ejecuta | Verificar step() en env |
| API 500 error | Modelo no cargado | Entrenar primero con train_agent.py |
| Observación vacía | Todas proficiencias < 0.5 | Iniciar con proficiencias más altas |
| Memory overflow | Demasiados entornos paralelos | Reducir n_envs o batch_size |
| Nodo no recomendado | No existe generador | Agregar en GENERATOR_MAP |
| Mismo ejercicio repetido | No se actualiza last_exercise_id | Verificar lógica en step() |

---

## 🚀 TABLA 12: Mejoras Prioritarias

| # | Mejora | Impacto | Dificultad | Tiempo | Prioridad |
|---|--------|---------|-----------|--------|-----------|
| 1 | Recompensa multi-temporal | Alto | Media | 1 día | 🔴 |
| 2 | Detección de plateau | Alto | Media | 1 día | 🔴 |
| 3 | Epsilon adaptativo | Alto | Baja | 4h | 🔴 |
| 4 | Transfer learning | Medio | Alta | 3 días | 🟡 |
| 5 | Student embeddings | Medio | Alta | 2 días | 🟡 |
| 6 | Curriculum learning | Medio | Media | 1 día | 🟡 |
| 7 | A/B Testing | Medio | Baja | 2 días | 🟡 |
| 8 | SHAP explicabilidad | Bajo | Media | 1 día | 🟢 |
| 9 | xAPI integration | Bajo | Media | 2 días | 🟢 |
| 10 | Multi-agent RL | Bajo | Alta | 1 semana | 🟢 |

---

## 📁 TABLA 13: Estructura de Carpetas

| Ruta | Contenido | Importante |
|------|-----------|------------|
| `ia_drl_engine/` | Código principal | ✅ Core |
| `├── train_agent.py` | Entrenar PPO | 🎯 Ejecutar primero |
| `├── train_bc.py` | Entrenar BC | Alternativa |
| `├── evaluate_agent.py` | Evaluar modelo | 📊 Post-entrenamiento |
| `├── main.py` | API FastAPI | 🌐 Producción |
| `├── src/env/` | Entorno Gymnasium | 🧠 Core RL |
| `├── src/agents/` | Carga e inferencia | 🎯 Recomendaciones |
| `├── src/generators/` | Crear ejercicios | 🎼 Generación |
| `├── src/simulator/` | Datos sintéticos | 📊 Entrenamiento |
| `├── models/` | Modelos guardados | 💾 Checkpoints |
| `├── data/` | Datos y grafo | 📁 Recursos |
| `└── notebooks/` | Análisis Jupyter | 📈 Visualización |

---

## 🔗 TABLA 14: URLs de Desarrollo

| Recurso | URL | Puerto | Descripción |
|---------|-----|--------|------------|
| **API Docs** | `http://localhost:8000/docs` | 8000 | Swagger UI interactivo |
| **API Redoc** | `http://localhost:8000/redoc` | 8000 | Documentación alternativa |
| **TensorBoard** | `http://localhost:6006` | 6006 | Gráficas entrenamiento |
| **Jupyter** | `http://localhost:8888` | 8888 | Notebooks análisis |

---

## 📚 TABLA 15: Documentación Generada

| Archivo | Tipo | Páginas | Secciones | Para Quién |
|---------|------|---------|-----------|-----------|
| **RESUMEN_EJECUTIVO_DRL** | Overview | 5 | 12 | Ejecutivos, nuevos |
| **ANALISIS_DRL_ENGINE** | Técnico | 15 | 10 | Devs, scientists |
| **DIAGRAMAS_DRL_ENGINE** | Visual | 10 | 10 | Visual learners |
| **GUIA_PRACTICA_DRL** | How-to | 12 | 10 | Implementadores |
| **MEJORAS_FUTURAS_DRL** | Research | 15 | 10 | Researchers |

---

## ⏱️ TABLA 16: Tiempos Típicos

| Actividad | Tiempo |
|-----------|--------|
| Leer RESUMEN | 15 min |
| Leer ANALISIS completo | 45 min |
| Ver DIAGRAMAS | 30 min |
| Seguir GUIA instalación | 10 min |
| Ejecutar data_generator | 10 min |
| Entrenar PPO (10k steps) | 5-10 min |
| Consulta API | < 100 ms |
| Generar ejercicio | 50-100 ms |
| Sesión (9 ejercicios) | 15-20 min |

---

## 🎯 TABLA 17: Métricas de Éxito

| Métrica | Esperado | Actual | Estado |
|---------|----------|--------|--------|
| **Reward promedio / ep** | 12-16 | TBD | ❓ |
| **Tasa éxito ejercicios** | 65-75% | TBD | ❓ |
| **Respeto prerequisitos** | 100% | ✅ | ✅ |
| **Evita repeticiones** | 95%+ | ✅ | ✅ |
| **Escalado dificultad** | Gradual | ✅ | ✅ |
| **Latencia API** | < 100ms | ~50ms | ✅ |
| **Uptime servidor** | 99%+ | TBD | ❓ |

---

## 💡 TABLA 18: Preguntas Frecuentes - Ubicación

| Pregunta | Documento | Sección |
|----------|-----------|---------|
| ¿Cómo funciona el sistema? | RESUMEN | §1-2 |
| ¿Qué es la función de recompensa? | ANALISIS | §5 |
| ¿Cómo veo el flujo? | DIAGRAMAS | §1-3 |
| ¿Cómo instalo? | GUIA | §1 |
| ¿Cómo entreno? | GUIA | §3 |
| ¿Cómo uso el API? | GUIA | §5 |
| ¿Cómo debuggeo? | GUIA | §9 |
| ¿Qué puedo mejorar? | MEJORAS | §1-10 |

---

## 🎓 TABLA 19: Próximos Pasos

| Orden | Tarea | Tiempo | Dependencias |
|-------|-------|--------|---|
| 1 | Leer RESUMEN | 15 min | - |
| 2 | Leer ANALISIS | 45 min | 1 |
| 3 | Revisar DIAGRAMAS | 30 min | 1-2 |
| 4 | Instalar dependencias | 10 min | 3 |
| 5 | Generar datos | 10 min | 4 |
| 6 | Entrenar modelo | 10 min | 5 |
| 7 | Evaluar modelo | 5 min | 6 |
| 8 | Iniciar API | 5 min | 6 |
| 9 | Test API | 5 min | 8 |
| 10 | Explorar mejoras | 60 min | 9 |

**Tiempo total**: ~3-4 horas

---

## 📞 TABLA 20: Contacto y Recursos

| Recurso | Ubicación | Tipo |
|---------|-----------|------|
| **Código fuente** | `ia_drl_engine/` | GitHub |
| **Documentación** | `ANALISIS_*.md` | Markdown |
| **Ejemplos** | `GUIA_*.md` | Code |
| **Datos** | `data/` | JSON/JSONL |
| **Modelos** | `models/` | .zip |
| **Tests** | `tests/` | Python |
| **Notebooks** | `notebooks/` | Jupyter |

---

**Generado**: Mayo 2026  
**Proyecto**: Tesis de Maestría - IA Musical  
**Autor**: Vicente Alves, UACH

