import json
from ia_drl_engine.src.utils.path_utils import resolve_path

def load_skill_mapping():
    path = resolve_path("@data/graph/nodes.json")

    with open(path) as f:
        data = json.load(f)

    nodes = data["nodes"]

    def sort_key(node):
        node_id = node["id"]
        number = int(node_id[:-1])
        letter = node_id[-1]
        return (number, letter)

    sorted_nodes = sorted(nodes, key=sort_key)

    skill_to_idx = {}
    idx_to_skill = {}
    ordered_skills = []

    for i, node in enumerate(sorted_nodes):
        skill_id = node["id"]
        skill_to_idx[skill_id] = i
        idx_to_skill[i] = skill_id
        ordered_skills.append(skill_id)

    return skill_to_idx, idx_to_skill, ordered_skills