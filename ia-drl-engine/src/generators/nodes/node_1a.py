# src/generators/nodes/node_1a.py

import random
from typing import Dict, Any, List
import json
import base64
from io import BytesIO
# from vexflow import VexFlowRenderer, Stave, StaveNote, Voice, Formatter # Comentado, no se usa en este scope

# ----------------------------------------------------------------------
# --- CONSTANTES DEL NODO 1A: Duración y Valor Rítmico (Compás 4/4) ---
# ----------------------------------------------------------------------
FIGURES_BASIC = {
    "Negra": "q",
    "Blanca": "h",
    "Corchea": "8",
    "Silencio_N": "qr",
    "Redonda": "w"
}

FIGURES_DURATION = {
    "q": 1.0,    # Quarter note = 1 beat
    "h": 2.0,    # Half note = 2 beats
    "8": 0.5,    # Eighth note = 1/2 beat
    "qr": 1.0,   # Quarter rest = 1 beat
    "w": 4.0,    # Whole note = 4 beats
    "16": 0.25,  # Sixteenth note = 1/4 beat
    "32": 0.125  # Thirty-second note = 1/8 beat
}

TIME_SIGNATURE = "4/4"
MAX_TIME = 4.0 # Cuatro tiempos

# ----------------------------------------------------------------------
# --- FUNCIONES AUXILIARES (Sin cambios en lógica interna) ---
# ----------------------------------------------------------------------

def _generate_1a_rhythm_pattern(difficulty: int) -> List[str]:
    """
    Algoritmo generador de patrones rítmicos válidos para 4/4.
    Asegura variedad y progresión de dificultad.
    """
    
    figures_map = {
        1: [FIGURES_BASIC['Negra'], FIGURES_BASIC['Blanca']], # Negras y Blancas
        2: [FIGURES_BASIC['Negra'], FIGURES_BASIC['Corchea'], FIGURES_BASIC['Silencio_N']], # + Corcheas y Silencio
        3: [FIGURES_BASIC['Negra'], FIGURES_BASIC['Corchea'], FIGURES_BASIC['Blanca'], FIGURES_BASIC['Silencio_N']], # Mezcla figuras
    }
    
    figures_list = figures_map.get(difficulty, figures_map[3])
    pattern: List[str] = []
    current_duration = 0.0
    
    while current_duration < MAX_TIME:
        # Filtra figuras que no excedan el límite del compás (4 tiempos)
        possible_figures = [f for f in figures_list if current_duration + FIGURES_DURATION[f] <= MAX_TIME]
        
        # Evita finalizar con un silencio o un tiempo incompleto si es posible
        if (MAX_TIME - current_duration) == 1.0 and FIGURES_BASIC['Negra'] in possible_figures:
            next_figure = FIGURES_BASIC['Negra']
        elif not possible_figures:
            break
        else:
            next_figure = random.choice(possible_figures)
            
        pattern.append(next_figure)
        current_duration += FIGURES_DURATION[next_figure]
        
    return pattern

def _generate_1a_theory(difficulty: int) -> Dict[str, Any]:
    """Genera ejercicios teóricos sobre valor y duración."""
    
    if difficulty == 1:
        # Foco: Valor simple de figura
        figure, symbol = random.choice([(k, v) for k, v in FIGURES_BASIC.items() if k in ['Negra', 'Blanca']])
        duration = FIGURES_DURATION[symbol]
        question = f"¿Cuántos tiempos vale la figura de **{figure}** ({symbol}) en un compás de {TIME_SIGNATURE}?"
        answer = f"{duration} tiempo(s)"
    
    elif difficulty == 2:
        # Foco: Suma de valores o equivalencias Corchea/Negra
        
        exercise_type = random.choice(['Suma', 'Equivalencia'])
        
        if exercise_type == 'Suma':
            fig1, fig2 = random.sample(['Negra', 'Corchea', 'Silencio_N'], 2)
            sym1, sym2 = FIGURES_BASIC[fig1], FIGURES_BASIC[fig2]
            val1, val2 = FIGURES_DURATION[sym1], FIGURES_DURATION[sym2]
            
            question = f"Si juntas una **{fig1}** ({sym1}) y una **{fig2}** ({sym2}), ¿cuál es la duración total en tiempos?"
            answer = f"{val1 + val2} tiempos"
        else: # Equivalencia
            question = "¿Cuántas figuras de **Corchea** ({FIGURES_BASIC['Corchea']}) se necesitan para igualar el valor de una **Blanca** ({FIGURES_BASIC['Blanca']})?"
            answer = "Cuatro Corcheas (4 * 0.5 = 2 tiempos)"
            
    else: # Dificultad 3: Compás completo o figura más larga
        
        exercise_type = random.choice(['Compás', 'Patrón_Valor'])
        
        if exercise_type == 'Compás':
            figure = random.choice(['Redonda', 'Blanca'])
            symbol = FIGURES_BASIC[figure]
            question = f"¿Cuántas figuras de **{figure}** ({symbol}) caben en un compás completo de {TIME_SIGNATURE}?"
            answer = str(int(MAX_TIME / FIGURES_DURATION[symbol]))
        else: # Valor total de un patrón
            pattern = _generate_1a_rhythm_pattern(2)
            total_duration = sum(FIGURES_DURATION[f] for f in pattern)
            question = f"Calcula el valor total en tiempos del siguiente patrón: {' '.join(pattern)}"
            answer = f"{total_duration} tiempos"

    return {
        "node": "1A", "type": "teorico", "difficulty": difficulty,
        "exercise": question, "expected_answer": answer,
        "presentation_format": "text_input" 
    }

def _generate_1a_practical(difficulty: int) -> Dict[str, Any]:
    """Genera ejercicios prácticos (ejecución/ritmo)."""
    
    pattern = _generate_1a_rhythm_pattern(difficulty)
    rhythm_string = " ".join(pattern)
    task = f"Da palmadas o marca el ritmo siguiendo este patrón en compás de {TIME_SIGNATURE}: {rhythm_string}"
    
    return {
        "node": "1A", "type": "practico", "difficulty": difficulty,
        "exercise": task, "rhythm_sequence": pattern, 
        "expected_answer": "El alumno debe reproducir el patrón en tiempo real.",
        "presentation_format": "rhythm_playback" 
    }

def _generate_1a_dictation(difficulty: int) -> Dict[str, Any]:
    """Genera ejercicios de dictado rítmico."""
    
    pattern = _generate_1a_rhythm_pattern(difficulty)
    rhythm_string = " ".join(pattern)
    task = f"Escucha la secuencia rítmica (en {TIME_SIGNATURE}) y escribe las figuras musicales que la componen."
    
    return {
        "node": "1A", "type": "dictado", "difficulty": difficulty,
        "exercise": task, 
        "audio_source": f"//path/to/audio/1a_D{difficulty}_{rhythm_string.replace(' ', '_')}.mp3", # Ruta simulada
        "expected_answer": pattern,
        "presentation_format": "rhythm_input_from_audio" 
    }

# ----------------------------------------------------------------------
# --- FUNCIÓN PRINCIPAL DEL NODO ---
# ----------------------------------------------------------------------

def generate_1a_exercise(difficulty: int, last_type: str = None) -> Dict[str, Any]:
    """
    Función principal que decide y genera un ejercicio para el Nodo 1A.
    :param difficulty: 1 (fácil), 2 (medio), 3 (difícil)
    :param last_type: El tipo de ejercicio anterior ('teorico', 'practico', 'dictado') para promover la variedad.
    :return: dict con el ejercicio generado.
    """

    # 1. Determinar el tipo de ejercicio, priorizando la variedad
    available_types = ["teorico", "practico", "dictado"]
    
    # Evitar la repetición inmediata del mismo tipo
    if last_type in available_types:
        available_types.remove(last_type)
        
    # Si solo queda uno o no había previo, volvemos a las opciones originales
    if not available_types: available_types = ["teorico", "practico", "dictado"]
    exercise_type = random.choice(available_types)

    # 2. Generar y devolver el ejercicio
    if exercise_type == "teorico":
        return _generate_1a_theory(difficulty)
    elif exercise_type == "practico":
        return _generate_1a_practical(difficulty)
    elif exercise_type == "dictado":
        return _generate_1a_dictation(difficulty)
    
    raise ValueError("Error interno en la selección de tipo de ejercicio.")

# Función para generar un MIDI de prueba (reemplaza con tu lógica real)
def generate_dummy_midi() -> bytes:
    # Crea un MIDI de ejemplo (esto debe ser reemplazado con tu lógica real)
    # Usaremos una cadena de bytes simple como placeholder
    dummy_midi_header = b'MThd\x00\x00\x00\x06\x00\x01\x00\x01\x00@'
    dummy_midi_track = b'MTrk\x00\x00\x00\x04\x00\xff/\x00'
    return dummy_midi_header + dummy_midi_track

def generate_vexflow_notes(rhythm_pattern: List[str]) -> List[Dict[str, str]]:
    """Genera datos de notas VexFlow a partir de un patrón rítmico."""
    note_mapping = {
        "q": {"keys": ["c/4"], "duration": "q"},     # Negra
        "h": {"keys": ["c/4"], "duration": "h"},     # Blanca
        "8": {"keys": ["c/4"], "duration": "8"},     # Corchea
        "qr": {"keys": ["b/4"], "duration": "qr"},   # Silencio de negra
        "w": {"keys": ["c/4"], "duration": "w"},     # Redonda
        "16": {"keys": ["c/4"], "duration": "16"},   # Semicorchea
        "32": {"keys": ["c/4"], "duration": "32"}    # Fusa
    }

    notes = []
    for rhythm in rhythm_pattern:
        note_info = note_mapping.get(rhythm)
        if note_info:
            notes.append(note_info.copy())
    
    return notes

if __name__ == "__main__":
    import sys

    try:
        # Leer argumentos del sistema (si se pasan)
        difficulty = int(sys.argv[1]) if len(sys.argv) > 1 else 2
        exercise_type = sys.argv[2] if len(sys.argv) > 2 else None

        # Si se especifica tipo, forzamos ese tipo
        if exercise_type == "teorico":
            exercise = _generate_1a_theory(difficulty)
        elif exercise_type == "practico":
            exercise = _generate_1a_practical(difficulty)
        elif exercise_type == "dictado":
            exercise = _generate_1a_dictation(difficulty)
        else:
            exercise = generate_1a_exercise(difficulty)

        rhythm_pattern = (
            exercise.get("rhythm_sequence", [])
            if exercise["type"] in ["practico", "dictado"]
            else _generate_1a_rhythm_pattern(difficulty)
        )

        notes = generate_vexflow_notes(rhythm_pattern)
        midi_data = generate_dummy_midi()
        midi_data_base64 = base64.b64encode(midi_data).decode("utf-8")

        response = {
            "status": "success",
            "data": {
                "exercise": exercise,
                "presentation": {
                    "midiData": midi_data_base64,
                    "notes": notes,
                    "rhythmPattern": rhythm_pattern
                }
            }
        }

        print(json.dumps(response))

    except Exception as e:
        error_response = {
            "status": "error",
            "message": str(e)
        }
        print(json.dumps(error_response))
