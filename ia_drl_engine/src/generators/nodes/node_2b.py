import random
from typing import Dict, Any, List

def generate_vexflow_notes_scale(scale_type: str, root: str = "c/4", direction: str = "asc") -> List[Dict[str, str]]:
    # Generaliza para cualquier raíz, tipo y dirección
    semitone_map = {
        "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6,
        "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11
    }
    scale_formulas = {
        "mayor": [2,2,1,2,2,2,1],
        "menor": [2,1,2,2,1,2,2],
        "dórico": [2,1,2,2,2,1,2],
        "frigio": [1,2,2,2,1,2,2]
    }
    root_note, octave = root.split("/")
    octave = int(octave)
    root_base = root_note.capitalize().replace('b', 'b').replace('#', '#')
    root_semitone = semitone_map.get(root_base, 0)
    formula = scale_formulas.get(scale_type, scale_formulas["mayor"])
    notes = []
    current_semitone = root_semitone
    current_octave = octave
    notes.append(f"{root_base.lower()}/{current_octave}")
    for step in (formula if direction == "asc" else reversed(formula)):
        if direction == "asc":
            current_semitone += step
        else:
            current_semitone -= step
        note_octave = current_octave + (current_semitone // 12)
        current_semitone = current_semitone % 12
        # Buscar la nota correspondiente
        note_name = None
        for k, v in semitone_map.items():
            if v == current_semitone and len(k) == 1:
                note_name = k
                break
        if not note_name:
            for k, v in semitone_map.items():
                if v == current_semitone:
                    note_name = k
                    break
        notes.append(f"{note_name.lower()}/{note_octave}")
    return [
        {"keys": [n], "duration": "8"} for n in notes
    ]

def generate_2b_exercise(difficulty: int) -> Dict[str, Any]:
    # Dificultad ajusta tipo, raíz y dirección
    if difficulty == 1:
        scale_type = "mayor"
        root = "c/4"
        direction = "asc"
    elif difficulty == 2:
        scale_type = random.choice(["mayor", "menor"])
        root = random.choice(["c/4", "d/4", "e/4", "f/4", "g/4"])
        direction = random.choice(["asc", "desc"])
    elif difficulty == 3:
        scale_type = random.choice(["mayor", "menor", "dórico", "frigio"])
        root = random.choice(["c/4", "d/4", "e/4", "f/4", "g/4", "a/4", "b/4"])
        direction = random.choice(["asc", "desc"])
    else:
        # difficulty 4: modes and ambiguous tonalities, include more roots
        scale_type = random.choice(["dórico", "frigio", "locrio", "mixolidio", "lidio"])
        root = random.choice(["c/3", "d/3", "e/3", "f/3", "g/3", "a/3", "b/3"])
        direction = random.choice(["asc", "desc"])    
    notes = generate_vexflow_notes_scale(scale_type, root, direction)

    kind = random.choice(["identificacion", "modo_vs_escala", "formula"]) if difficulty < 3 else random.choice(["identificacion", "formula"])

    if kind == "identificacion":
        prompt = f"Identifica la escala: ¿Es {scale_type}, raíz {root.upper()}, {'ascendente' if direction=='asc' else 'descendente'}?"
        scale_pool = ["mayor", "menor", "dórico", "frigio"]
        distractors = [s for s in scale_pool if s != scale_type]
        random.shuffle(distractors)
        alternatives = [scale_type] + distractors[:3]
        correct = scale_type

    elif kind == "modo_vs_escala":
        prompt = "¿En qué se diferencia un modo musical de una escala?"
        alternatives = [
            "Un modo es una escala con un centro tonal diferente",
            "Un modo es siempre menor",
            "Un modo tiene más notas que una escala",
            "No hay diferencia"
        ]
        correct = alternatives[0]

    else:  # formula
        prompt = "¿Cuál es la estructura de tonos y semitonos de la escala mayor?"
        alternatives = ["2-2-1-2-2-2-1", "2-1-2-2-1-2-2", "1-2-2-2-1-2-2", "2-2-2-1-2-2-1"]
        correct = alternatives[0]

    random.shuffle(alternatives)
    correct_index = alternatives.index(correct)

    return {
        "node": "2B",
        "type": "teorico",
        "difficulty": difficulty,
        "exercise": prompt,
        "expected_answer": correct,
        "presentation_format": "multiple_choice",
        "data": {
            "notes": notes,
            "timeSignature": "4/4",
            "clef": "treble",
            "alternatives": alternatives,
            "correct_index": correct_index,
        },
    }