import csv
import json
import argparse
from ia_drl_engine.src.utils.path_utils import resolve_path
from ia_drl_engine.src.utils.skill_mapping import load_skill_mapping


FIXED_COLS = [
    'student_id', 'profile_type', 'step_number', 'session_id',
    'recommended_skill_id', 'outcome_success', 'outcome_score', 'outcome_time_spent', 'reward'
]


def parse_row(header, row, clamp=False, compact=False):
    # header: list of column names
    # row: list of string values
    data = dict(zip(header, row))

    # extract fixed fields
    student_id = data.get('student_id')
    profile_type = data.get('profile_type')
    step_number = int(data.get('step_number') or 0)
    session_id = data.get('session_id')
    recommended = data.get('recommended_skill_id')

    # parse outcome
    success = data.get('outcome_success')
    try:
        success = bool(int(success))
    except Exception:
        success = success in ['True', 'true', '1']

    try:
        score = float(data.get('outcome_score') or 0.0)
    except Exception:
        score = 0.0

    try:
        time_spent = int(float(data.get('outcome_time_spent') or 0))
    except Exception:
        time_spent = 0

    try:
        reward = float(data.get('reward') or 0.0)
    except Exception:
        reward = 0.0

    # detect skill columns
    skill_cols = [c for c in header if c not in FIXED_COLS]

    skill_proficiency = {}

    # compact mode: skills_compact column contains concatenated 3-digit ints per skill
    if compact and 'skills_compact' in header:
        compact_str = data.get('skills_compact') or ''
        _, _, ordered_skills = load_skill_mapping()
        # chunk into 3-digit groups
        chunks = [compact_str[i:i+3] for i in range(0, len(compact_str), 3)]
        for s, ch in zip(ordered_skills, chunks):
            try:
                val = int(ch)
            except Exception:
                val = 0
            v = val / 100.0
            if clamp:
                v = max(0.0, min(1.0, v))
            skill_proficiency[s] = v

    else:
        for s in skill_cols:
            # ignore non-skill columns
            if s in FIXED_COLS:
                continue
            raw = data.get(s, '')
            try:
                val = float(raw)
            except Exception:
                val = 0.0
            # if values are in 0-100 integers, convert
            if abs(val) > 1.0:
                val = val / 100.0
            if clamp:
                val = max(0.0, min(1.0, val))
            skill_proficiency[s] = val

    entry = {
        'student_id': student_id,
        'profile_type': profile_type,
        'step_number': step_number,
        'session_id': session_id,
        'state': {
            'skill_proficiency': skill_proficiency,
            'frustration_level': 0
        },
        'action': {'recommended_skill_id': recommended},
        'outcome': {'success': success, 'score': score, 'time_spent': time_spent},
        'reward': reward
    }

    return entry


def convert(input_path, output_path, clamp=False, compact=False):
    input_path = resolve_path(input_path)
    output_path = resolve_path(output_path)

    with open(input_path, 'r', encoding='utf-8') as f_in, open(output_path, 'w', encoding='utf-8') as f_out:
        reader = csv.reader(f_in)
        header = next(reader)
        for row in reader:
            if not any(row):
                continue
            entry = parse_row(header, row, clamp=clamp, compact=compact)
            f_out.write(json.dumps(entry, ensure_ascii=False) + '\n')

    print(f'Converted {input_path} -> {output_path}.')


def main():
    parser = argparse.ArgumentParser(description='Convert CSV synthetic dataset to JSONL compatible with train_bc.py')
    parser.add_argument('--input', required=True, help='CSV input path (can use @ prefix)')
    parser.add_argument('--output', required=True, help='JSONL output path (can use @ prefix)')
    parser.add_argument('--clamp', action='store_true', help='Clamp skill proficiencies to [0,1] before converting')
    parser.add_argument('--compact', action='store_true', help='Treat input as compact (skills_compact column)')

    args = parser.parse_args()
    convert(args.input, args.output, clamp=args.clamp, compact=args.compact)


if __name__ == '__main__':
    main()
