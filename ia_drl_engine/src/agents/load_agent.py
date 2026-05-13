from pathlib import Path
from stable_baselines3 import PPO
import logging
import os
import threading
import torch
import sys
import types

logger = logging.getLogger(__name__)

# Ruta base (repositorio)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Allow overriding model path with env var (useful for Render or mounted volumes)
MODEL_PATH = Path(os.environ.get("MODEL_PATH", str(BASE_DIR / "models" / "ppo_music_learning.zip")))

# Lazy singleton with lock to avoid races when the first request loads the model
_model = None
_model_lock = threading.Lock()


def get_model():
    """Return a singleton PPO model loaded to CPU.

    - Loads lazily on first call. Thread-safe via a lock to avoid double loads.
    - Forces loading on CPU to avoid CUDA attempts on deployment platforms without GPUs.
    - Environment variable MODEL_PATH can override the path inside the container.
    """
    global _model
    if _model is not None:
        return _model

    with _model_lock:
        if _model is not None:
            return _model

        model_path_str = str(MODEL_PATH)
        logger.info(f"Loading model from {model_path_str} ...")
        if not Path(model_path_str).exists():
            logger.error(f"Model path does not exist: {model_path_str}")
            raise FileNotFoundError(model_path_str)

        try:
            # Limit CPU threads to reduce memory/CPU usage on small instances
            os.environ.setdefault("OMP_NUM_THREADS", os.environ.get("OMP_NUM_THREADS", "1"))
            os.environ.setdefault("MKL_NUM_THREADS", os.environ.get("MKL_NUM_THREADS", "1"))
            os.environ.setdefault("OPENBLAS_NUM_THREADS", os.environ.get("OPENBLAS_NUM_THREADS", "1"))
            try:
                torch.set_num_threads(int(os.environ.get("OMP_NUM_THREADS", "1")))
            except Exception:
                pass
            # Workaround: some models serialized with older numpy builds refer to
            # module paths like "numpy._core.numeric" which don't exist on newer
            # numpy distributions. cloudpickle will try to import that name when
            # deserializing. Provide a runtime shim so imports succeed.
            try:
                import numpy._core.numeric  # noqa: F401 - prefer real module when present
            except Exception:
                try:
                    import numpy.core.numeric as _numeric
                    shim = types.ModuleType("numpy._core.numeric")
                    shim.__dict__.update(_numeric.__dict__)
                    sys.modules["numpy._core.numeric"] = shim
                    logger.debug("Inserted shim module for numpy._core.numeric to support legacy pickles")
                except Exception as _shim_exc:
                    # If creating the shim fails, continue and surface the original
                    # error when loading the model so the caller can troubleshoot.
                    logger.debug(f"Failed to install numpy._core.numeric shim: {_shim_exc}")
            # stable-baselines3 supports device argument; ensure CPU
            _model = PPO.load(model_path_str, device="cpu")
            logger.info("Model loaded successfully (device=cpu)")
            return _model
        except Exception:
            logger.exception(f"Failed to load model from {model_path_str}")
            raise


def is_model_loaded() -> bool:
    """Return True if the model is already loaded in memory (does not attempt to load)."""
    return _model is not None and Path(MODEL_PATH).exists()
