from fastapi import FastAPI
from ia_drl_engine.middleware import register_logging_middleware

"""
Nota: originalmente importábamos `setup_endpoints` desde `ia_drl_engine.endpoints`.
Para usar los endpoints integrados (incluye /activation/list y /activation/toggle)
importamos desde `ia_drl_engine.endpoints_integrated`.
"""
from ia_drl_engine.endpoints_integrated import setup_endpoints, NextExerciseRequest, SessionEndRequest

app = FastAPI()

# Register logging middleware (logs method, path and body)
register_logging_middleware(app)
# =========================================
# ROOT
# =========================================

@app.get("/")
def root():
    return {
        "message": "DRL Learning Engine API running",
        "endpoints": [
            "POST /next-exercise - Recomienda ejercicio con soporte focus nodes",
            "POST /session-end - Calcula recompensa de sesión"
        ]
    }

# =========================================
# SETUP ENDPOINTS
# =========================================

setup_endpoints(app)


@app.get("/health")
def health():
    """Basic health check. Returns model_loaded flag (doesn't load model)."""
    from ia_drl_engine.src.agents.load_agent import is_model_loaded
    return {"status": "ok", "model_loaded": is_model_loaded(), "model_path_env": "MODEL_PATH"}
