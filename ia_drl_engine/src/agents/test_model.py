# test_model.py

from stable_baselines3 import PPO

model = PPO.load("../../models/ppo_music_learning")

print("Modelo cargado correctamente")
print("Observation space:", model.observation_space)
print("Action space:", model.action_space)