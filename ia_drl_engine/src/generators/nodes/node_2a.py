import os
import random
from typing import Dict, Any, List
import json

def generate_vexflow_notes_interval(interval: int, root: str = "c/4", direction: str = "asc") -> List[Dict[str, str]]:
    # Generaliza para cualquier raíz y dirección
    semitone_map = {
        "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6,
        "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11
    }
    root_note, octave = root.split("/")
    octave = int(octave)
    root_base = root_note.capitalize().replace('b', 'b').replace('#', '#')
    root_semitone = semitone_map.get(root_base, 0)
    if direction == "asc":
        target_semitone = root_semitone + interval
    else:
        target_semitone = root_semitone - interval
    note_octave = octave + (target_semitone // 12)
    target_semitone = target_semitone % 12
    # Buscar la nota correspondiente
    note_name = None
    for k, v in semitone_map.items():
        if v == target_semitone and len(k) == 1:
            note_name = k
            break
    if not note_name:
        for k, v in semitone_map.items():
            if v == target_semitone:
                note_name = k
                break
    note2 = f"{note_name.lower()}/{note_octave}"
    return [
        {"keys": [root], "duration": "q"},
        {"keys": [note2], "duration": "q"}
    ]

def generate_2a_exercise(difficulty: int) -> Dict[str, Any]:
    # Prefer question bank entries (randomized) and fallback to procedural
    def _load_question_bank(node_name: str = "node_2a") -> List[Dict[str, Any]]:
        bank_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "question_banks", f"{node_name}_questions.json"))
        try:
            with open(bank_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "questions" in data and isinstance(data["questions"], list):
                return data["questions"]
        except Exception:
            return []
        return []

    bank = _load_question_bank("node_2a")
    candidates = [q for q in bank if int(q.get("difficulty", difficulty)) == difficulty] if bank else []
    if candidates:
        q = random.choice(candidates)
        # accept multiple possible field names from question banks
        prompt = q.get("exercise") or q.get("question") or q.get("prompt") or ""
        alternatives = q.get("alternatives") or q.get("options") or []
        if alternatives:
            correct = q.get("correct") or q.get("expected_answer") or q.get("answer")
            random.shuffle(alternatives)
            correct_index = 0
            if correct is not None:
                cstr = str(correct)
                for idx, alt in enumerate(alternatives):
                    try:
                        if str(alt) == cstr:
                            correct_index = idx
                            break
                    except Exception:
                        continue
            else:
                correct_index = q.get("correct_index", 0)
        else:
            alternatives = []
            correct_index = q.get("correct_index", 0)
        data = q.get("data", {}) or {}
        if alternatives:
            data["alternatives"] = alternatives
            data["correct_index"] = correct_index

        # Ensure we always return a non-empty prompt and an expected_answer.
        # Some banks may provide alternatives but omit a textual prompt or the
        # explicit expected_answer; in that case derive them safely.
        out_prompt = prompt or q.get("prompt") or q.get("question") or q.get("exercise") or "Selecciona la alternativa correcta."
        out_expected = q.get("expected_answer") or q.get("correct") or q.get("answer")
        if (out_expected is None or out_expected == "") and alternatives:
            # derive from correct_index (guard bounds)
            try:
                ci = int(correct_index)
            except Exception:
                ci = 0
            if 0 <= ci < len(alternatives):
                out_expected = alternatives[ci]
            else:
                out_expected = alternatives[0]

        return {
            "node": "2A",
            "type": q.get("type", "teorico"),
            "difficulty": difficulty,
            "exercise": out_prompt,
            "expected_answer": out_expected,
            "presentation_format": q.get("presentation_format", "multiple_choice"),
            "data": data
        }

    # Dificultad ajusta el rango, raíz y dirección
    if difficulty == 1:
        interval = random.randint(1, 3)
        root = "c/4"
        direction = "asc"
    elif difficulty == 2:
        interval = random.randint(1, 5)
        root = random.choice(["c/4", "d/4", "e/4", "f/4", "g/4"])
        direction = random.choice(["asc", "desc"])
    elif difficulty == 3:
        interval = random.randint(1, 8)
        root = random.choice(["c/4", "d/4", "e/4", "f/4", "g/4", "a/4", "b/4"])
        direction = random.choice(["asc", "desc"])
    else:  # difficulty 4: extended intervals and compound intervals
        interval = random.randint(1, 12)
        root = random.choice(["c/3", "d/3", "e/3", "f/3", "g/3", "a/3", "b/3"])  # lower roots
        direction = random.choice(["asc", "desc"]) 
    notes = generate_vexflow_notes_interval(interval, root, direction)

    # Choose a question style: identification or conceptual (inversion/definition)
    kind = random.choice(["identificacion", "inversion", "definicion"]) if difficulty < 3 else random.choice(["identificacion", "inversion"])

    if kind == "identificacion":
        prompt = f"¿Qué intervalo {'ascendente' if direction=='asc' else 'descendente'} hay entre las dos notas? (Raíz: {root.upper()})"
        candidates = [interval, max(1, interval-1), interval+1]
        # add one random distractor further away
        extra = random.randint(1, max(12, interval+5))
        if extra not in candidates:
            candidates.append(extra)
        random.shuffle(candidates)
        alternatives = [str(c) for c in candidates[:4]]
        correct = str(interval)

    elif kind == "inversion":
        # Inversión simple: semitonos de la inversión (octava=12 semitonos)
        inv = (12 - interval) % 12
        prompt = f"Si invertimos este intervalo, ¿cuántos semitonos tendrá la inversión?"
        options = [inv, max(0, inv-1), (inv+1) % 12, (inv+2) % 12]
        random.shuffle(options)
        alternatives = [str(o) for o in options]
        correct = str(inv)

    else:  # definicion
        prompt = "¿Cuál es la definición de intervalo en música?"
        alternatives = [
            "La distancia entre dos notas medida en semitonos",
            "La duración de una nota en compás",
            "Un tipo de acorde de tres notas",
            "La velocidad a la que se interpreta una pieza"
        ]
        correct = alternatives[0]

    # Decide if we should include a rendered score for this exercise
    include_notes = kind in ("identificacion", "inversion")

    # Ensure alternatives are shuffled and compute correct index
    random.shuffle(alternatives)
    correct_index = alternatives.index(correct)

    result = {
        "node": "2A",
        "type": "teorico",
        "difficulty": difficulty,
        "exercise": prompt,
        "expected_answer": correct,
        "presentation_format": "multiple_choice",
        "data": {
            "timeSignature": "4/4",
            "clef": "treble",
            "alternatives": alternatives,
            "correct_index": correct_index,
        },
    }

    if include_notes:
        # attach the pre-generated notes to the payload
        result["data"]["notes"] = notes

    return result