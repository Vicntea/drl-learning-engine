# drl_inference.py
from stable_baselines3 import PPO
import numpy as np
from ia_drl_engine.state_model import UserState
from ia_drl_engine.exercise_schema import Exercise
from ia_drl_engine.src.generators.nodes import node_1a  # Import all node modules as needed

# --- Singleton Model Loader ---
class DRLModelSingleton:
    _model = None

    @classmethod
    def get_model(cls, model_path="models/ppo_music_learning.zip"):
        if cls._model is None:
            cls._model = PPO.load(model_path)
        return cls._model

# --- Exercise Catalog Loader ---
def load_exercise_catalog():
    catalog = []
    for diff in [1, 2, 3]:
        for last_type in [None, "teorico", "practico", "dictado"]:
            ex = node_1a.generate_1a_exercise(diff, last_type)
            catalog.append(Exercise(
                exercise_id=ex.get("exercise_id", f"1A_{diff}_{last_type}"),
                node=ex["node"],
                difficulty=ex["difficulty"],
                type=ex["type"],
                estimated_time=1.0,  # Placeholder
                prerequisites=[]
            ))
    return catalog

EXERCISE_CATALOG = load_exercise_catalog()

# --- State Transformation ---
def state_to_vector(state: UserState) -> np.ndarray:
    nodes = ["notes", "rhythm", "intervals", "scales", "chords"]
    vec = []
    for k in nodes:
        vec.append(state.knowledge.get(k, 0.0))
    for k in nodes:
        vec.append(state.accuracy.get(k, 0.0))
    for k in nodes:
        vec.append(state.attempts.get(k, 0))
    vec.append(state.streak)
    vec.append(state.last_exercise_difficulty)
    vec.append(state.time_since_last_practice)
    return np.array(vec, dtype=np.float32)

# --- Inference Function ---
def get_next_exercise(state: UserState) -> Exercise:
    model = DRLModelSingleton.get_model()
    obs = state_to_vector(state)
    action, _ = model.predict(obs, deterministic=True)
    exercise = EXERCISE_CATALOG[action]
    return exercise

# --- Optional: Update User State ---
def update_user_state(state: UserState, result: dict) -> UserState:
    node = result["node"]
    correct = result["correct"]
    state.attempts[node] += 1
    prev_acc = state.accuracy[node]
    state.accuracy[node] = ((prev_acc * (state.attempts[node] - 1)) + int(correct)) / state.attempts[node]
    if correct:
        state.knowledge[node] = min(1.0, state.knowledge[node] + 0.05)
        state.streak += 1
    else:
        state.knowledge[node] = max(0.0, state.knowledge[node] - 0.02)
        state.streak = 0
    return state
