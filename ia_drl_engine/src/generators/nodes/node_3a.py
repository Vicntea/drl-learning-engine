import random
from typing import Dict, Any, List

def generate_vexflow_notes_chord(chord_type: str, root: str = "c/4") -> List[Dict[str, str]]:
    # Fórmulas de intervalos para cada tipo de acorde
    semitone_map = {
        "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6,
        "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11
    }
    chord_formulas = {
        "mayor": [0, 4, 7],
        "menor": [0, 3, 7],
        "aumentado": [0, 4, 8],
        "disminuido": [0, 3, 6],
        "séptima": [0, 4, 7, 10],
        "menor séptima": [0, 3, 7, 10],
        "mayor séptima": [0, 4, 7, 11],
        "séptima disminuida": [0, 3, 6, 9]
    }
    # Extraer nota raíz y octava
    root_note, octave = root.split("/")
    octave = int(octave)
    root_base = root_note.capitalize().replace('b', 'b').replace('#', '#')
    root_semitone = semitone_map.get(root_base, 0)
    formula = chord_formulas.get(chord_type, chord_formulas["mayor"])
    notes = []
    for interval in formula:
        semitone = (root_semitone + interval) % 12
        note_octave = octave + ((root_semitone + interval) // 12)
        # Buscar la nota correspondiente
        note_name = None
        for k, v in semitone_map.items():
            if v == semitone and len(k) == 1:  # Prefiere notas naturales
                note_name = k
                break
        if not note_name:
            for k, v in semitone_map.items():
                if v == semitone:
                    note_name = k
                    break
        notes.append(f"{note_name.lower()}/{note_octave}")
    return [
        {"keys": notes, "duration": "h"}
    ]

def generate_3a_exercise(difficulty: int) -> Dict[str, Any]:
    # Dificultad ajusta el tipo de acorde
    if difficulty == 1:
        chord_type = "mayor"
    elif difficulty == 2:
        chord_type = random.choice(["mayor", "menor", "aumentado", "disminuido"])
    elif difficulty == 3:
        chord_type = random.choice([
            "mayor", "menor", "aumentado", "disminuido",
            "séptima", "menor séptima"
        ])
    else:
        chord_type = random.choice([
            "mayor", "menor", "aumentado", "disminuido",
            "séptima", "menor séptima", "mayor séptima", "séptima disminuida",
            "7sus4", "add9"
        ])
    root = random.choice(["c/4", "d/4", "e/4", "f/4", "g/4", "a/4", "b/4"])
    notes = generate_vexflow_notes_chord(chord_type, root)

    kind = random.choice(["identificacion", "funcion", "inversion"]) if difficulty < 3 else random.choice(["identificacion", "inversion"])

    if kind == "identificacion":
        prompt = f"¿Qué tipo de acorde es este? (Raíz: {root.upper()})"
        chord_types_pool = [
            "mayor", "menor", "aumentado", "disminuido",
            "séptima", "menor séptima", "mayor séptima", "séptima disminuida"
        ]
        distractors = [c for c in chord_types_pool if c != chord_type]
        random.shuffle(distractors)
        alternatives = [chord_type] + distractors[:3]
        correct = chord_type

    elif kind == "funcion":
        prompt = "¿Cuál es la función armónica básica de un acorde de tónica?"
        alternatives = ["Tónica", "Dominante", "Subdominante", "Sustituta"]
        correct = alternatives[0]

    else:  # inversion
        prompt = "¿Qué indica la inversión de un acorde?"
        alternatives = [
            "Cambio en la nota de bajo del acorde",
            "Un tipo de escala",
            "Que el acorde es disminuido",
            "Que la tonalidad ha cambiado"
        ]
        correct = alternatives[0]

    random.shuffle(alternatives)
    correct_index = alternatives.index(correct)

    return {
        "node": "3A",
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