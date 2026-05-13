from ia_drl_engine.src.utils.skill_mapping import load_skill_mapping

skill_to_idx, idx_to_skill, ordered_skills = load_skill_mapping()

print("=== ORDERED SKILLS ===")

for i, skill in enumerate(ordered_skills):
    print(i, "->", skill)