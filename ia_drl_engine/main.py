from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Any, Dict

app = FastAPI()

# Modelo de entrada para el estado del estudiante
default_state = {"student_id": 1, "current_level": "1a", "score": 0}

class StudentState(BaseModel):
    student_id: int
    current_level: str
    score: int
    # Puedes agregar más campos según tu modelo

# Dummy DRL agent (reemplaza por tu lógica real)
def drl_agent_decision(state: Dict[str, Any]) -> Dict[str, Any]:
    # Aquí deberías llamar a tu agente DRL real
    # Por ahora, devolvemos una recomendación dummy
    return {
        "next_exercise": f"exercise_for_{state['current_level']}",
        "recommended_level": state["current_level"],
        "reason": "Dummy recommendation. Replace with DRL agent output."
    }

@app.post("/next-exercise")
def next_exercise(state: StudentState):
    # Llama al agente DRL (dummy en esta versión)
    recommendation = drl_agent_decision(state.dict())
    return {"recommendation": recommendation}

@app.get("/")
def root():
    return {"message": "DRL Learning Engine API running. Use /next-exercise endpoint."}
