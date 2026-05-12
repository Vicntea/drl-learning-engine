import gymnasium as gym
from gymnasium import spaces

# --- DRL MusicLearningEnv with UserState integration ---
from ia_drl_engine.state_model import UserState
from ia_drl_engine.exercise_schema import Exercise

class MusicLearningEnv(gym.Env):
    """
    DRL environment for music learning with structured user state and exercise catalog.
    """
    metadata = {"render_modes": ["human"]}

    def __init__(self, exercise_catalog, max_steps=50):
        super().__init__()
        self.exercise_catalog = exercise_catalog
        self.node_ids = list({ex.node for ex in exercise_catalog})
        self.n_nodes = len(self.node_ids)
        self.node_prereqs = {ex.node: ex.prerequisites for ex in exercise_catalog}
        self.max_steps = max_steps
        self.current_step = 0
        self.state = None
        self.last_exercise_id = None

    def reset(self, initial_state=None, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = 0
        if initial_state is not None:
            self.state = initial_state
        else:
            self.state = UserState(
                knowledge=dict.fromkeys(self.node_ids, 0.0),
                accuracy=dict.fromkeys(self.node_ids, 0.0),
                attempts=dict.fromkeys(self.node_ids, 0),
                streak=0,
                last_exercise_difficulty=1,
                time_since_last_practice=0.0,
                recent_performance_trend={nid: [] for nid in self.node_ids}
            )
        self.last_exercise_id = None
        return self._get_obs(), {}

    def step(self, action, correct, response_time):
        self.current_step += 1
        if not (0 <= action < len(self.exercise_catalog)):
            raise ValueError("Acción fuera de rango")
        exercise = self.exercise_catalog[action]
        node = exercise.node
        # Prerequisite enforcement
        if exercise.prerequisites:
            if not all(self.state.knowledge.get(pr, 0.0) > 0.6 for pr in exercise.prerequisites):
                return self._get_obs(), -1.0, False, False, {"reason": "Prerequisites not met"}
        # No repeated exercises
        if exercise.exercise_id == self.last_exercise_id:
            return self._get_obs(), -0.5, False, False, {"reason": "Repeated exercise"}
        # Update attempts
        self.state.attempts[node] += 1
        prev_acc = self.state.accuracy[node]
        self.state.accuracy[node] = (
            (prev_acc * (self.state.attempts[node] - 1) + int(correct)) / self.state.attempts[node]
        )
        # Update knowledge
        if correct:
            self.state.knowledge[node] = min(1.0, self.state.knowledge[node] + 0.05)
            self.state.streak += 1
        else:
            self.state.knowledge[node] = max(0.0, self.state.knowledge[node] - 0.02)
            self.state.streak = 0
        # Update last exercise difficulty
        self.state.last_exercise_difficulty = exercise.difficulty
        # Update recent performance trend
        self.state.recent_performance_trend[node].append(int(correct))
        if len(self.state.recent_performance_trend[node]) > 10:
            self.state.recent_performance_trend[node].pop(0)
        # Update time since last practice
        self.state.time_since_last_practice = 0
        self.last_exercise_id = exercise.exercise_id
        # Reward
        reward = self.calculate_reward(correct, node, exercise.difficulty)
        # Termination
        done = self.current_step >= self.max_steps or all(v >= 0.95 for v in self.state.knowledge.values())
        info = {"exercise_id": exercise.exercise_id, "node": node}
        return self._get_obs(), reward, done, False, info

    def calculate_reward(self, correct, node, difficulty):
        trend = self.state.recent_performance_trend[node]
        prev = trend[-2:] if len(trend) > 1 else [0, 0]
        improvement = int(correct) - prev[-1] if prev else 0
        ideal_difficulty = int(self.state.knowledge[node] * 10)
        diff_gap = abs(difficulty - ideal_difficulty)
        # Exploración: bonifica nodos poco practicados y ejercicios nuevos
        nodo_poco_practicado = self.state.attempts[node] < 3
        ejercicio_nuevo = len(trend) <= 1
        reward = 1.0 * int(correct)
        if improvement:
            reward += 0.5
        if diff_gap <= 1:
            reward += 0.5  # Explota el nivel óptimo
        elif diff_gap > 2:
            reward -= 0.3  # Penaliza saltos grandes
        if nodo_poco_practicado:
            reward += 0.2  # Bonifica explorar nodos débiles
        if ejercicio_nuevo:
            reward += 0.1  # Bonifica variedad
        return reward

    def render(self):
        print(f"Current state: {self.state}")
        print(f"Step: {self.current_step}")

    def _get_obs(self):
        return self.state