import os

def resolve_path(custom_path):
    """
    Convierte rutas con '@' en rutas absolutas basadas en ia_drl_engine/
    """
    if custom_path.startswith("@"):
        # 📍 subir hasta ia_drl_engine
        base_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../")
        )

        return os.path.join(base_dir, custom_path[1:])

    return custom_path