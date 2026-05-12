# debug_actions.py
from ia_drl_engine.src.agents.inference import (
    state_to_observation
)

from ia_drl_engine.src.agents.load_agent import (
    get_model
)

model = get_model()

states = [

    {
        "skill_proficiency": {
            "1a": 0.0,
            "2a": 0.0,
            "2b": 0.0,
            "3a": 0.0
        }
    },

    {
        "skill_proficiency": {
            "1a": 1.0,
            "2a": 0.0,
            "2b": 0.0,
            "3a": 0.0
        }
    },

    {
        "skill_proficiency": {
            "1a": 1.0,
            "2a": 1.0,
            "2b": 0.0,
            "3a": 0.0
        }
    },

    {
        "skill_proficiency": {
            "1a": 1.0,
            "2a": 1.0,
            "2b": 1.0,
            "3a": 1.0
        }
    }

]

for i, state in enumerate(states):

    obs = state_to_observation(state)

    action, _ = model.predict(obs)

    print(f"\nSTATE {i+1}")
    print(obs)
    print("ACTION:", action)
