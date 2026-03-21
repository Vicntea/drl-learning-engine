from concurrent.futures import ProcessPoolExecutor
import json
import random
import os

# --- Rutas y carga del árbol musical (igual que antes) ---
GRAPH_PATH = '../../data/graph/nodes.json'
OUTPUT_PATH = '../../data/synthetic/synthetic_data.jsonl'

def load_musical_tree(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

musical_tree = load_musical_tree(GRAPH_PATH)
nodes = musical_tree['nodes']
edges = musical_tree['edges']
node_ids = {node['id'] for node in nodes}

prerequisites = {node_id: [] for node_id in node_ids}
for edge in edges:
    prerequisites[edge['target']].append(edge['source'])

def get_all_prerequisites(node_id, prerequisites):
    all_prereqs = set()
    def dfs(current):
        for pr in prerequisites.get(current, []):
            if pr not in all_prereqs:
                all_prereqs.add(pr)
                dfs(pr)
    dfs(node_id)
    return all_prereqs

def get_node_level(node_id):
    return int(node_id[0])

def initialize_student_proficiency(profile_type):
    proficiency = {node_id: 0.0 for node_id in node_ids}
    if profile_type == "desde_cero":
        for node_id in node_ids:
            level = get_node_level(node_id)
            if level <= 2:
                proficiency[node_id] = random.uniform(0.1, 0.4)
    elif profile_type == "parcial":
        for node_id in ["3a", "3b", "4a", "4b"]:
            proficiency[node_id] = random.uniform(0.5, 0.8)
    elif profile_type == "avanzado":
        advanced_nodes = ["3a","3b","4a","4b","5a","6a","6b","7a","7b"]
        for node_id in advanced_nodes:
            proficiency[node_id] = random.uniform(0.4, 0.9)
    return proficiency

# --- Clase SyntheticStudent (igual que tu código anterior) ---
class SyntheticStudent:
    def __init__(self, student_id, profile_type="desde_cero", base_learning_rate=0.5, base_frustration_threshold=3):
        self.student_id = student_id
        self.learning_rate = base_learning_rate * random.uniform(0.7, 1.3)
        self.frustration_threshold = max(1, int(base_frustration_threshold * random.uniform(0.7, 1.5)))
        self.skill_proficiency = initialize_student_proficiency(profile_type)
        self.path_history = []
        self.elapsed_time_on_skills = {}
        self.failed_attempts = {node_id: 0 for node_id in node_ids}
        self.profile_type = profile_type
        if random.random() < 0.1:
            self.learning_rate *= 0.6
            self.frustration_threshold = max(1, self.frustration_threshold - 1)
        self.frustration_level = random.randint(0, 2)

    def get_state(self):
        return {
            "skill_proficiency": self.skill_proficiency.copy(),
            "path_history": self.path_history.copy(),
            "elapsed_time_on_skills": self.elapsed_time_on_skills.copy(),
            "frustration_level": self.frustration_level
        }

    def update_state(self, skill_id, outcome):
        current_level = self.skill_proficiency[skill_id]
        all_prereqs = get_all_prerequisites(skill_id, prerequisites)

        if outcome["success"]:
            prereq_levels = [self.skill_proficiency[p] for p in all_prereqs]
            if prereq_levels:
                avg_prereq = sum(prereq_levels) / len(prereq_levels)
                if avg_prereq < 0.3:
                    improvement = self.learning_rate * 0.3
                elif avg_prereq < 0.8:
                    improvement = self.learning_rate * 0.6
                else:
                    improvement = self.learning_rate
            else:
                improvement = self.learning_rate

            self.skill_proficiency[skill_id] = min(1.0, current_level + (1 - current_level) * improvement)
            self.failed_attempts[skill_id] = 0
            self.frustration_level = max(0, self.frustration_level - 1)
            for pr in all_prereqs:
                self.skill_proficiency[pr] = min(1.0, self.skill_proficiency[pr] + self.learning_rate * 0.25)
        else:
            self.failed_attempts[skill_id] += 1
            self.frustration_level += 1
            penalty_multiplier = 0.3 + 0.2 * (self.failed_attempts[skill_id] - 1)
            self.skill_proficiency[skill_id] = max(-0.2, current_level - self.learning_rate * penalty_multiplier)
            for pr in all_prereqs:
                if self.skill_proficiency[pr] < 0.8:
                    self.skill_proficiency[pr] = min(0.8, self.skill_proficiency[pr] + self.learning_rate * 0.1)

        self.elapsed_time_on_skills[skill_id] = self.elapsed_time_on_skills.get(skill_id, 0) + outcome["time_spent"]
        if skill_id not in self.path_history:
            self.path_history.append(skill_id)

    def choose_action(self):
        available_skills = [
            node_id for node_id in node_ids
            if self.skill_proficiency[node_id] <= 0.0
            and all(self.skill_proficiency[pr] >= 0.3 for pr in get_all_prerequisites(node_id, prerequisites))
        ]
        neighbor_skills = set()
        for node_id, proficiency in self.skill_proficiency.items():
            if proficiency >= 0.5:
                for edge in edges:
                    if edge['source'] == node_id and self.skill_proficiency[edge['target']] <= 0.0:
                        neighbor_skills.add(edge['target'])
        revisit_skills = [
            node_id for node_id in node_ids
            if 0.0 < self.skill_proficiency[node_id] < 1.0 or self.skill_proficiency[node_id] < 0.0
        ]
        if self.profile_type == "desde_cero":
            low_level_skills = [n for n in node_ids if get_node_level(n) <= 2 and self.skill_proficiency[n] < 0.8]
            if low_level_skills:
                return random.choice(low_level_skills)
        if neighbor_skills and random.random() < 0.7:
            return random.choice(list(neighbor_skills))
        elif available_skills:
            if any(self.skill_proficiency[n] < 0 for n in node_ids):
                if random.random() < 0.5:
                    return random.choice(revisit_skills)
            return random.choice(available_skills)
        elif revisit_skills:
            return random.choice(revisit_skills)
        else:
            return random.choice(list(node_ids))

def simulate_outcome(skill_id, student):
    all_prereqs = get_all_prerequisites(skill_id, prerequisites)
    prereq_levels = [student.skill_proficiency[p] for p in all_prereqs]
    if prereq_levels:
        avg_prereq = sum(prereq_levels) / len(prereq_levels)
        if avg_prereq < 0.3:
            base_success = 0.3
        elif avg_prereq < 0.8:
            base_success = 0.6
        else:
            base_success = 0.85
    else:
        base_success = (student.skill_proficiency.get(skill_id, 0.0) + 1.0) / 2.0
    adjusted_success = max(0.2, base_success - 0.03 * student.frustration_level)
    success = random.random() < adjusted_success
    score = random.uniform(0.7, 1.0) if success else random.uniform(0.1, 0.6)
    time_spent = random.randint(60, 300)
    return {"success": success, "score": round(score, 2), "time_spent": time_spent}

def calculate_reward(outcome, current_proficiency):
    if outcome["success"]:
        return 8.0 + (1.0 - current_proficiency) * 4
    else:
        return -7.0 - (current_proficiency + 1.0) * 5

# --- Función para simular un estudiante completo ---
def simulate_student(student_index):
    profile_type = "desde_cero" if student_index < 500 else "parcial" if student_index < 1000 else "avanzado"
    student = SyntheticStudent(f"sint_{student_index:04d}", profile_type=profile_type)
    session_counter = 0
    max_steps = 1300
    steps_per_session = 20
    student_records = []

    for j in range(max_steps):
        if all(student.skill_proficiency[n] >= 1.0 for n in node_ids):
            break
        if j % steps_per_session == 0:
            session_counter += 1
        current_state = student.get_state()
        recommended_skill = student.choose_action()
        outcome = simulate_outcome(recommended_skill, student)
        reward = calculate_reward(outcome, current_state["skill_proficiency"].get(recommended_skill, 0.0))
        student.update_state(recommended_skill, outcome)
        student_records.append({
            "student_id": student.student_id,
            "session_id": f"ses_{student.student_id}_{session_counter}",
            "state": current_state,
            "action": {"recommended_skill_id": recommended_skill},
            "outcome": outcome,
            "reward": reward
        })
    return student_records

# --- Generación de datos en paralelo ---
def generate_synthetic_data_parallel():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    total_students = 1500
    all_records = []

    with ProcessPoolExecutor() as executor:
        for student_records in executor.map(simulate_student, range(total_students)):
            all_records.extend(student_records)

    # Guardar en un solo archivo JSONL
    with open(OUTPUT_PATH, 'w') as f:
        for record in all_records:
            f.write(json.dumps(record) + "\n")

    print(f"Datos sintéticos generados en paralelo en {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_synthetic_data_parallel()
