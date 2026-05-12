# src/generators/nodes/node_1a.py

import random
from typing import Dict, Any, List
import json
import base64
from io import BytesIO

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
        # Usar comparación tolerante para floats
        if abs((MAX_TIME - current_duration) - 1.0) < 1e-9 and FIGURES_BASIC['Negra'] in possible_figures:
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
    # Generamos sólo ejercicios teóricos (variedad de tipos con alternativas)
    exercise_kind = random.choice([
        "valor_simple",
        "suma",
        "equivalencia",
        "compas",
        "rest_meaning",
        "compare_values",
    ])

    if exercise_kind == "valor_simple":
        figure = random.choice([k for k in FIGURES_BASIC.keys() if k in ["Negra", "Blanca", "Corchea", "Redonda"]])
        symbol = FIGURES_BASIC[figure]
        correct = str(FIGURES_DURATION[symbol])
        question = f"¿Cuántos tiempos vale la figura {figure} ({symbol}) en un compás de {TIME_SIGNATURE}?"
        # Build numeric alternatives
        options = [correct]
        # nearby numeric distractors
        nearby = [max(0.25, FIGURES_DURATION[symbol] + d) for d in [-1.0, -0.5, 0.5, 1.0]]
        for v in nearby:
            s = str(v)
            if s not in options:
                options.append(s)

    elif exercise_kind == "suma":
        fig1, fig2 = random.sample(["Negra", "Corchea", "Blanca"], 2)
        s1, s2 = FIGURES_BASIC[fig1], FIGURES_BASIC[fig2]
        val1, val2 = FIGURES_DURATION[s1], FIGURES_DURATION[s2]
        correct = str(val1 + val2)
        question = f"Si juntas {fig1} ({s1}) y {fig2} ({s2}), ¿cuántos tiempos suman?"
        options = [correct]
        # distractors: swap or +/- 0.5
        distract = [str(max(0.25, val1)), str(max(0.25, val2)), str(max(0.25, val1 + val2 + 0.5))]
        for d in distract:
            if d not in options:
                options.append(d)

    elif exercise_kind == "equivalencia":
        # Example: cuántas corcheas equivalen a una blanca
        base = "Corchea"
        target = "Blanca"
        symbol_base = FIGURES_BASIC[base]
        symbol_target = FIGURES_BASIC[target]
        correct = str(int(FIGURES_DURATION[symbol_target] / FIGURES_DURATION[symbol_base]))
        question = f"¿Cuántas {base}s ({symbol_base}) equivalen a una {target} ({symbol_target})?"
        options = [correct, str(int(correct)+1), str(int(correct)-1 if int(correct)>1 else 1), str(int(correct)+2)]

    else:  # compas
        figure = random.choice(["Redonda", "Blanca", "Negra"])
        symbol = FIGURES_BASIC[figure]
        correct = str(int(MAX_TIME / FIGURES_DURATION[symbol]))
        question = f"¿Cuántas figuras de {figure} ({symbol}) caben en un compás de {TIME_SIGNATURE}?"
        options = [correct, str(max(1, int(correct)-1)), str(int(correct)+1), str(int(correct)+2)]

    # Additional conceptual type: meaning of a rest or compare durations
    if exercise_kind == "rest_meaning":
        # Ask what a rest symbol indicates
        question = "¿Qué indica un silencio en una partitura?"
        correct = "Pausa en la emisión sonora durante una duración específica"
        options = [
            correct,
            "Tocar más fuerte durante la figura",
            "Repetir la nota anterior",
            "Cambiar la armadura de clave"
        ]

    if exercise_kind == "compare_values":
        # Compare two figures' durations
        f1, f2 = random.sample(["Negra", "Blanca", "Corchea", "Redonda"], 2)
        s1, s2 = FIGURES_BASIC[f1], FIGURES_BASIC[f2]
        v1, v2 = FIGURES_DURATION[s1], FIGURES_DURATION[s2]
        question = f"¿Cuál de las siguientes afirmaciones es correcta respecto a {f1} ({s1}) y {f2} ({s2})?"
        if v1 > v2:
            correct = f"{f1} dura más que {f2}"
        elif v1 < v2:
            correct = f"{f2} dura más que {f1}"
        else:
            correct = f"Ambas duran lo mismo"
        options = [correct, "Ambas son silencios", "Ninguna de las anteriores", "Son equivalentes en cualquier compás"]

    # Ensure 4 alternatives and shuffle
    options = list(dict.fromkeys(options))  # unique preserve order
    while len(options) < 4:
        # add plausible numeric filler
        filler = str(random.choice([0.5, 1.0, 2.0, 3.0]))
        if filler not in options:
            options.append(filler)
    random.shuffle(options)
    correct_index = options.index(correct)

    # Build VexFlow notes depending on exercise kind
    if exercise_kind in ("suma", "compas", "compare_values"):
        # show one or two notes representing the figures
        notes = []
        if exercise_kind == "suma":
            # represent two quarter/eighth/half notes
            notes = generate_vexflow_notes([FIGURES_BASIC.get(fig1, 'q'), FIGURES_BASIC.get(fig2, 'q')])
        else:
            notes = generate_vexflow_notes([FIGURES_BASIC.get(figure, 'q')])
    else:
        # simple example note for identification/equivalence
        notes = [{"keys": ["c/4"], "duration": "q"}]

    data = {
        "notes": notes,
        "timeSignature": TIME_SIGNATURE,
        "clef": "treble",
        "alternatives": options,
        "correct_index": correct_index
    }

    return {
        "node": "1A",
        "type": "teorico",
        "difficulty": difficulty,
        "exercise": question,
        "expected_answer": correct,
        "presentation_format": "multiple_choice",
        "data": data,
    }

def _generate_1a_practical(difficulty: int) -> Dict[str, Any]:
    """Genera ejercicios prácticos (ejecución/ritmo)."""
    
    pattern = _generate_1a_rhythm_pattern(difficulty)
    rhythm_string = " ".join(pattern)
    task = f"Da palmadas o marca el ritmo siguiendo este patrón en compás de {TIME_SIGNATURE}: {rhythm_string}"
    notes = generate_vexflow_notes(pattern)
    data = {
        "notes": notes,
        "timeSignature": TIME_SIGNATURE,
        "clef": "treble"
    }
    # Build alternatives: represent sequences as strings
    correct = " ".join(pattern)
    distractors = []
    # Create 3 distractors by shuffling or making small modifications
    for _ in range(3):
        p = pattern.copy()
        random.shuffle(p)
        distractors.append(" ".join(p))
    alternatives = [correct] + distractors
    random.shuffle(alternatives)
    correct_index = alternatives.index(correct)
    data["alternatives"] = alternatives
    data["correct_index"] = correct_index

    return {
        "node": "1A", "type": "practico", "difficulty": difficulty,
        "exercise": task, "rhythm_sequence": pattern,
        "expected_answer": "El alumno debe reproducir el patrón en tiempo real.",
        "presentation_format": "rhythm_playback",
        "data": data
    }

def _generate_1a_dictation(difficulty: int) -> Dict[str, Any]:
    """Genera ejercicios de dictado rítmico."""
    
    pattern = _generate_1a_rhythm_pattern(difficulty)
    rhythm_string = " ".join(pattern)
    task = f"Escucha la secuencia rítmica (en {TIME_SIGNATURE}) y escribe las figuras musicales que la componen."
    notes = generate_vexflow_notes(pattern)
    data = {
        "notes": notes,
        "timeSignature": TIME_SIGNATURE,
        "clef": "treble"
    }
    # Alternatives: include the correct pattern and modified variants
    correct = " ".join(pattern)
    distractors = []
    allowed_figures = list(FIGURES_BASIC.values()) + ["16", "32"]
    for _ in range(3):
        p = pattern.copy()
        if p:
            idx = random.randrange(len(p))
            p[idx] = random.choice(allowed_figures)
        distractors.append(" ".join(p))
    alternatives = [correct] + distractors
    random.shuffle(alternatives)
    correct_index = alternatives.index(correct)
    data["alternatives"] = alternatives
    data["correct_index"] = correct_index

    return {
        "node": "1A", "type": "dictado", "difficulty": difficulty,
        "exercise": task,
        "audio_source": f"//path/to/audio/1a_D{difficulty}_{rhythm_string.replace(' ', '_')}.mp3", # Ruta simulada
        "expected_answer": pattern,
        "presentation_format": "rhythm_input_from_audio",
        "data": data
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

    # Siempre generamos ejercicios teóricos (multiple-choice) para 1A
    return _generate_1a_theory(difficulty)

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
