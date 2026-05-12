from pathlib import Path
from stable_baselines3 import PPO
import logging

logger = logging.getLogger(__name__)

# Ruta absoluta segura
BASE_DIR = Path(__file__).resolve().parent.parent.parent

MODEL_PATH = BASE_DIR / "models" / "ppo_music_learning.zip"

# Carga perezosa del modelo: no cargar en import time para evitar fallos en la
# inicialización de la app si el modelo falta o tarda mucho en cargarse.
_model = None

def get_model():
    global _model
    if _model is not None:
        return _model

    try:
        model_path_str = str(MODEL_PATH)
        logger.info(f"Loading model from {model_path_str} ...")
        _model = PPO.load(model_path_str)
        logger.info("Model loaded successfully")
        return _model
    except Exception:
        logger.exception(f"Failed to load model from {MODEL_PATH}")
        # Re-raise so callers can handle gracefully
        raise