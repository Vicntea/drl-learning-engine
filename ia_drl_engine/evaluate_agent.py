import os
from dotenv import load_dotenv

from stable_baselines3 import PPO
from ia_drl_engine.src.env.music_learning_env import MusicLearningEnv


# 📁 Cargar variables de entorno (opcional)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../_envFiles/config.env"))


# 📁 Resolver rutas correctamente
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

graph_path = os.path.join(BASE_DIR, "data", "graph", "nodes.json")
model_path = os.path.join(BASE_DIR, "models", "ppo_music_learning")


# 🎯 Crear entorno
def create_env():
    return MusicLearningEnv(nodes_path=graph_path)


env = create_env()


# 🤖 Cargar modelo
if not os.path.exists(model_path + ".zip"):
    raise FileNotFoundError(
        f"El modelo entrenado no se encontró en {model_path}. Entrénalo primero."
    )

model = PPO.load(model_path)


# 🚀 Evaluación
EPISODES = 10

for episode in range(EPISODES):
    obs, info = env.reset()

    terminated = False
    truncated = False
    total_reward = 0

    print(f"\nEpisodio {episode + 1}")

    while not (terminated or truncated):
        action, _ = model.predict(obs, deterministic=True)

        obs, reward, terminated, truncated, info = env.step(action)

        total_reward += reward
        env.render()

    print(f"Recompensa total: {total_reward}")


print("\nEvaluación completada.")