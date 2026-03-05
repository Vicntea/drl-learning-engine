# 🎵 Tesis Musical con Deep Reinforcement Learning  
### *Modelo de IA para enseñanza musical personalizada*

---

## 🧠 Descripción del Proyecto

Este proyecto desarrolla un **modelo de Inteligencia Artificial** basado en **Deep Reinforcement Learning (DRL)** orientado a la **enseñanza personalizada de teoría musical**.  
El objetivo es crear un **entrenador adaptativo**, capaz de ajustar la **dificultad**, el **ritmo** y la **ruta de aprendizaje** según el progreso del estudiante.

El agente navega por un **árbol de conceptos musicales**, optimizando la enseñanza mediante retroalimentación continua.  
Inicialmente se entrena con **datos sintéticos**, y posteriormente se refina con **datos reales** obtenidos de pruebas piloto, buscando una **educación musical adaptativa y eficaz**. 🎼

---

## 🏗️ Estructura del Proyecto

Este repositorio sigue una **estructura modular y reproducible**, ideal para proyectos de Machine Learning.

```bash
tesis-musical-RL/
│
├── env/                   # 🌱 Archivos para reproducir el entorno
│   └── environment.yml    # Configuración (Conda/Pip)
│
├── data/                  # 🎵 Datos sintéticos y reales (anonimizados)
│   ├── synthetic/
│   └── pilot/
│
├── models/                # 🤖 Modelos entrenados y checkpoints
│   ├── baseline/          # Baselines (heurísticas)
│   └── rl_agent/          # Versiones entrenadas del agente
│
├── export/                # 📦 Modelos exportados (TensorFlow.js, etc.)
│
├── notebooks/             # 📓 Experimentación y análisis (Jupyter)
│
├── src/                   # 🧩 Código fuente principal
│   ├── generators/        # Generadores de ejercicios musicales
│   │   ├── base.py        # Funciones base y utilidades
│   │   └── nodes/         # Algoritmos específicos por nodo del árbol
│   ├── simulator/         # Simulador de estudiantes y generador de datos
│   ├── env/               # Entorno Gym RL
│   ├── agents/            # Algoritmos y configuración de agentes DRL
│   └── utils/             # Funciones auxiliares
│
├── tests/                 # 🧪 Pruebas unitarias
│
├── docs/                  # 📚 Documentación (MkDocs / Sphinx)
│
├── README.md              # 📝 Descripción general del proyecto
├── LICENSE                # ⚖️ Licencia (MIT / GPL)
└── .gitignore             # 🚫 Ignorar data pesada y checkpoints
