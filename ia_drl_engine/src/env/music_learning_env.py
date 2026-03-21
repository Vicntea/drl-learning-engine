import gymnasium as gym
from gymnasium import spaces
import numpy as np
import json
import os
from ia_drl_engine.src.utils.path_utils import resolve_path


class MusicLearningEnv(gym.Env):
    """
    Entorno Gymnasium para la progresión de un estudiante en un grafo de aprendizaje musical.
    """

    metadata = {"render_modes": ["human"]}

    def __init__(self, nodes_path=None, max_steps=50):
        super().__init__()

        # 📁 Resolver path
        if nodes_path is None:
            nodes_path = resolve_path("@data/graph/nodes.json")

        if not os.path.exists(nodes_path):
            raise FileNotFoundError(f"No se encontró el archivo: {nodes_path}")

        # 📊 Cargar grafo
        with open(nodes_path, "r") as f:
            data = json.load(f)

        self.nodes = data["nodes"]
        self.edges = data["edges"]

        self.node_ids = [n["id"] for n in self.nodes]
        self.n_nodes = len(self.node_ids)

        # 🔗 Lista de adyacencia
        self.adj = {nid: [] for nid in self.node_ids}
        for edge in self.edges:
            self.adj[edge["source"]].append(edge["target"])

        # 🎯 Espacios
        self.observation_space = spaces.MultiBinary(self.n_nodes)
        self.action_space = spaces.Discrete(self.n_nodes)

        # ⏱️ Control de episodio
        self.max_steps = max_steps
        self.current_step = 0

        # Estado
        self.current_node_idx = 0
        self.visited = set()

    # 🔄 RESET (Gymnasium API)
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.current_node_idx = 0
        self.visited = {self.current_node_idx}
        self.current_step = 0

        return self._get_obs(), {}

    # ▶️ STEP (Gymnasium API)
    def step(self, action):
        self.current_step += 1

        if not self.action_space.contains(action):
            raise ValueError("Acción fuera de rango")

        current_node_id = self.node_ids[self.current_node_idx]
        next_node_id = self.node_ids[action]

        valid_next = next_node_id in self.adj[current_node_id]

        # 🎯 Reward shaping (clave para aprendizaje)
        if valid_next:
            reward = 1.0

            # Bonus por nodo no visitado
            if action not in self.visited:
                reward += 0.5

            self.current_node_idx = action
            self.visited.add(action)

        else:
            reward = -1.0  # penalización

        # 🏁 Condiciones de término
        no_more_moves = len(self.adj[self.node_ids[self.current_node_idx]]) == 0

        terminated = no_more_moves
        truncated = self.current_step >= self.max_steps

        return self._get_obs(), reward, terminated, truncated, {}

    # 👁️ Render
    def render(self):
        print(f"Nodo actual: {self.node_ids[self.current_node_idx]}")
        print(f"Visitados: {[self.node_ids[i] for i in self.visited]}")
        print(f"Paso: {self.current_step}")

    # 🧠 Observación
    def _get_obs(self):
        obs = np.zeros(self.n_nodes, dtype=np.int8)
        obs[self.current_node_idx] = 1
        return obs


# 🧪 Test standalone
if __name__ == "__main__":
    env = MusicLearningEnv()

    obs, info = env.reset()
    terminated = False
    truncated = False
    total_reward = 0

    while not (terminated or truncated):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        env.render()
        total_reward += reward

    print(f"Episodio terminado. Recompensa total: {total_reward}")