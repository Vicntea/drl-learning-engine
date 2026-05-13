import numpy as np

from ia_drl_engine.src.agents.load_agent import get_model

from ia_drl_engine.src.utils.skill_mapping import load_skill_mapping

# =========================================
# GENERATORS
# =========================================

from ia_drl_engine.src.generators.nodes.node_1a import generate_1a_exercise
from ia_drl_engine.src.generators.nodes.node_2a import generate_2a_exercise
from ia_drl_engine.src.generators.nodes.node_2b import generate_2b_exercise
from ia_drl_engine.src.generators.nodes.node_3a import generate_3a_exercise
from ia_drl_engine.src.utils.activation import get_enabled_nodes

# =========================================
# SKILL MAPPING
# =========================================

skill_to_idx, idx_to_skill, ordered_skills = load_skill_mapping()

# =========================================
# GENERATOR MAP
# =========================================

GENERATOR_MAP = {
    "1a": generate_1a_exercise,
    "2a": generate_2a_exercise,
    "2b": generate_2b_exercise,
    "3a": generate_3a_exercise
}

# =========================================
# STATE -> OBSERVATION
# =========================================

def state_to_observation(student_state):

    """
    Convierte el estado del alumno
    al formato esperado por PPO.

    PPO espera:
    MultiBinary(23)
    """

    obs = np.zeros(len(ordered_skills), dtype=np.int8)

    skill_proficiency = student_state.get(
        "skill_proficiency",
        {}
    )

    for skill, value in skill_proficiency.items():

        if skill in skill_to_idx and value >= 0.5:

            idx = skill_to_idx[skill]

            obs[idx] = 1

    return obs

# =========================================
# DIFFICULTY HEURISTIC
# =========================================

def calculate_difficulty(student_state, selected_skill):

    proficiency = student_state.get(
        "skill_proficiency",
        {}
    ).get(selected_skill, 0)

    # Map proficiency [0..1] to difficulty levels 1..4
    # Lower proficiency -> easier exercise
    if proficiency < 0.25:
        return 1
    elif proficiency < 0.5:
        return 2
    elif proficiency < 0.75:
        return 3
    else:
        return 4

# =========================================
# MAIN INFERENCE
# =========================================

def predict_next_exercise(student_state):

    model = get_model()

    # ---------------------------------
    # OBSERVATION
    # ---------------------------------

    obs = state_to_observation(student_state)

    # ---------------------------------
    # PPO ACTION
    # ---------------------------------

    action, _ = model.predict(obs)

    selected_skill = idx_to_skill[int(action)]

    # Filter: if chosen skill is not enabled, pick a fallback among enabled
    enabled = get_enabled_nodes()
    if selected_skill not in enabled:
        # try to pick the model action if it's enabled; else choose a random enabled
        # fallback to 1a if nothing enabled
        enabled_list = [s for s in GENERATOR_MAP.keys() if s in enabled]
        selected_skill = enabled_list[0] if enabled_list else "1a"

    # ---------------------------------
    # FALLBACK
    # PPO podría elegir nodos
    # que aún no implementas
    # ---------------------------------

    if selected_skill not in GENERATOR_MAP:

        selected_skill = "1a"

    # ---------------------------------
    # DIFFICULTY
    # ---------------------------------

    difficulty = calculate_difficulty(
        student_state,
        selected_skill
    )

    # ---------------------------------
    # GENERATOR
    # ---------------------------------

    generator_function = GENERATOR_MAP[selected_skill]

    exercise = generator_function(
        difficulty=difficulty
    )

    return {
        "recommended_node": selected_skill,
        "difficulty": difficulty,
        "exercise": exercise
    }   
print("INFERENCE LOADED")
print(predict_next_exercise)