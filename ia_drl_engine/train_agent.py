import os
from dotenv import load_dotenv

from ia_drl_engine.src.env.music_learning_env import MusicLearningEnv
from ia_drl_engine.src.utils.path_utils import resolve_path


from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env


# 📁 Cargar variables de entorno (opcional)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../_envFiles/config.env"))


# 📁 Resolver rutas correctamente (SIN hardcode)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

graph_path = resolve_path("@data/graph/nodes.json")
model_path = resolve_path("@models/ppo_music_learning")
tensorboard_path = resolve_path("@tensorboard")

# 🎯 Crear entorno
def create_env():
    return MusicLearningEnv(nodes_path=graph_path)


# 🧠 Vectorizar entorno
env = make_vec_env(create_env, n_envs=1)


# 🤖 Modelo PPO
model = PPO(
    policy="MlpPolicy",
    env=env,
    verbose=1,
    tensorboard_log=tensorboard_path
)


# 🚀 Entrenamiento
TIMESTEPS = 10000
model.learn(total_timesteps=TIMESTEPS)


# 💾 Guardar modelo
os.makedirs(os.path.dirname(model_path), exist_ok=True)
model.save(model_path)

print(f"Modelo entrenado y guardado en {model_path}")