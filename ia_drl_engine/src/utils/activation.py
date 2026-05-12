import json
from typing import Set
from ia_drl_engine.src.utils.path_utils import resolve_path


ACTIVATION_FILE = None


def _activation_path():
    global ACTIVATION_FILE
    if ACTIVATION_FILE:
        return ACTIVATION_FILE
    # place activation file next to graph nodes for convenience
    nodes_path = resolve_path("@data/graph/nodes.json")
    activation_path = nodes_path.replace("nodes.json", "activation.json")
    ACTIVATION_FILE = activation_path
    return ACTIVATION_FILE


def _load_nodes_json():
    path = resolve_path("@data/graph/nodes.json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data


def get_enabled_nodes() -> Set[str]:
    """Return set of enabled node ids.

    Priority:
    - If activation.json exists, read enabled list from it.
    - Else, fallback to nodes.json and return nodes where locked != true.
    """
    activation_path = _activation_path()
    try:
        with open(activation_path, encoding="utf-8") as f:
            d = json.load(f)
            enabled = set(d.get("enabled", []))
            return enabled
    except FileNotFoundError:
        data = _load_nodes_json()
        enabled = {n["id"] for n in data.get("nodes", []) if not n.get("locked", False)}
        return enabled


def set_node_enabled(node_id: str, enabled: bool):
    """Enable or disable a node in activation.json (creates file if missing)."""
    activation_path = _activation_path()
    try:
        with open(activation_path, encoding="utf-8") as f:
            d = json.load(f)
    except FileNotFoundError:
        d = {"enabled": []}

    enabled_set = set(d.get("enabled", []))
    if enabled:
        enabled_set.add(node_id)
    else:
        enabled_set.discard(node_id)

    d["enabled"] = sorted(enabled_set)
    with open(activation_path, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
