import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import subprocess
import json
import base64
import sys

app = FastAPI()

# Configurar CORS para permitir solicitudes desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Cambia según tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/exercise")
async def generate_exercise(difficulty: int = 2, type: str | None = None) -> Dict[str, Any]:
    """
    Genera un ejercicio del tipo especificado llamando al script node_1a.py.
    Ejemplo:
      /api/exercise?type=practico&difficulty=2
    """
    try:
        script_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "ia-drl-engine", "src", "generators", "nodes", "node_1a.py")
        )

        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Script no encontrado en la ruta: {script_path}")

        # Ejecutar el script pasando dificultad y tipo como argumentos
        args = [sys.executable, script_path, str(difficulty)]
        if type:
            args.append(type)

        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8"
        )

        json_output = result.stdout.strip()
        print("Salida estándar:", json_output)
        print("Errores del script:", result.stderr)

        if not json_output:
            raise ValueError("El script no devolvió una salida JSON válida.")

        data = json.loads(json_output)
        return data

    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el script:\n{e.stderr}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=f"Error en el generador de ejercicios: {e.stderr.strip()}")

    except FileNotFoundError as e:
        print(f"Archivo no encontrado: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))

    except json.JSONDecodeError as e:
        print(f"Error al parsear JSON: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail="Error al decodificar salida JSON del script.")

    except Exception as e:
        print(f"Error inesperado: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))
