import json
import random
import os
import math

# --- Rutas ---
GRAPH_PATH = '../../data/graph/nodes.json'
OUTPUT_PATH = '../../data/synthetic/synthetic_data.jsonl'

# --- Configuración de Simulación ---
TOTAL_STUDENTS = 1500
MAX_STEPS_PER_STUDENT = 160
STEPS_PER_SESSION = 9
MASTERY_THRESHOLD = 0.75
MAX_SIMULATION_MASTERY = 0.6

# --- Carga del grafo ---
def load_musical_tree(file_path):
    if not os.path.exists(file_path):
        print(f"Error: No se encontró el archivo del grafo en {file_path}")
        return {'nodes': [], 'edges': []}
    with open(file_path, 'r') as f:
        return json.load(f)

musical_tree = load_musical_tree(GRAPH_PATH)
nodes = musical_tree.get('nodes', [])
edges = musical_tree.get('edges', [])
node_ids = {node['id'] for node in nodes} if nodes else set()

# --- Prerrequisitos ---
prerequisites = {node_id: [] for node_id in node_ids}
for edge in edges:
    if edge['target'] in node_ids:
        prerequisites[edge['target']].append(edge['source'])

def get_all_prerequisites(node_id, prerequisites_map):
    all_prereqs = set()
    def dfs(current):
        for pr in prerequisites_map.get(current, []):
            if pr not in all_prereqs:
                all_prereqs.add(pr)
                dfs(pr)
    dfs(node_id)
    return all_prereqs

def get_node_level(node_id):
    try:
        return int(node_id[0])
    except (ValueError, IndexError):
        return 0

# --- Inicialización de perfiles ---
def initialize_student_proficiency(profile_type):
    proficiency = {node_id: 0.0 for node_id in node_ids}

    def set_proficiency_and_prereqs(node_id, min_val, max_val, factor=0.7):
        if proficiency[node_id] < min_val:
            proficiency[node_id] = random.uniform(min_val, max_val)
        for pr_id in get_all_prerequisites(node_id, prerequisites):
            pr_min = min(min_val * factor, 0.4)
            pr_max = max_val * factor
            current_pr = proficiency.get(pr_id, 0.0)
            if current_pr < pr_min:
                proficiency[pr_id] = random.uniform(pr_min, pr_max)

    if profile_type == "desde_cero":
        for node_id in node_ids:
            level = get_node_level(node_id)
            if level <= 2 and level > 0:
                proficiency[node_id] = random.uniform(0.1, 0.35)
            elif level > 2:
                proficiency[node_id] = random.uniform(0.01, 0.1)
    elif profile_type == "parcial":
        target_nodes = ["3a", "3b", "4a", "4b"]
        for node_id in target_nodes:
            if node_id in node_ids:
                set_proficiency_and_prereqs(node_id, 0.5, 0.8)
        for node_id in node_ids:
            if get_node_level(node_id) >= 5 and proficiency[node_id] == 0.0:
                proficiency[node_id] = random.uniform(0.1, 0.25)
    elif profile_type == "avanzado":
        advanced_nodes = ["3a","3b","4a","4b","5a","6a","6b","7a","7b"]
        for node_id in advanced_nodes:
            if node_id in node_ids:
                set_proficiency_and_prereqs(node_id, 0.6, 0.9)
        for node_id in node_ids:
            if proficiency[node_id] == 0.0:
                proficiency[node_id] = random.uniform(0.3, 0.5)

    return proficiency

# --- Clase SyntheticStudent ---
class SyntheticStudent:
    def __init__(self, student_id, profile_type="desde_cero", base_learning_rate=0.5, base_frustration_threshold=3):
        self.student_id = student_id
        self.learning_rate = base_learning_rate * random.uniform(0.9, 1.4)
        self.frustration_threshold = max(1, int(base_frustration_threshold * random.uniform(0.7, 1.5)))
        self.skill_proficiency = initialize_student_proficiency(profile_type)
        self.path_history = []
        self.elapsed_time_on_skills = {}
        self.failed_attempts = {node_id: 0 for node_id in node_ids}
        self.profile_type = profile_type
        self.frustration_level = random.randint(0, 2)
        self.consecutive_successes = {node_id: 0 for node_id in node_ids}
        self.skill_mastery = {node_id: min(1.0, prof * 0.8) for node_id, prof in self.skill_proficiency.items()}
        self.session_attempts = {node_id: 0 for node_id in node_ids}
        self.dominated_nodes = set()
        self.skill_consistency = {node_id: 0.0 for node_id in node_ids}

    def reset_session_tracking(self):
        self.session_attempts = {node_id: 0 for node_id in node_ids}
        self.frustration_level = max(0, self.frustration_level - 1)
        self.consecutive_successes = {node_id: 0 for node_id in node_ids}

    def get_state(self):
        return {
            "skill_proficiency": self.skill_proficiency.copy(),
            "path_history": self.path_history.copy(),
            "elapsed_time_on_skills": self.elapsed_time_on_skills.copy(),
            "frustration_level": self.frustration_level,
            "skill_mastery": self.skill_mastery.copy(),
        }

    def update_state(self, skill_id, outcome):
        current_level = self.skill_proficiency[skill_id]
        all_prereqs = get_all_prerequisites(skill_id, prerequisites)
        
        # Actualizar consistencia
        if outcome["success"]:
            self.skill_consistency[skill_id] = min(1.0, self.skill_consistency[skill_id] + 0.2)
        else:
            self.skill_consistency[skill_id] *= 0.7

        if outcome["success"]:
            consistency_bonus = self.skill_consistency[skill_id] * 0.3
            improvement_factor = self.learning_rate * (1.0 - current_level) * (0.8 + consistency_bonus)
            improvement = min(0.3, improvement_factor)
            new_level = min(1.0, current_level + improvement)
            self.skill_proficiency[skill_id] = new_level

            # Nodo dominado
            if new_level >= 0.8:
                self.dominated_nodes.add(skill_id)

                # --- Boost prerequisitos recursivo ---
                def boost_prerequisites(node, boost_level=0.9):
                    prereqs = get_all_prerequisites(node, prerequisites)
                    for pr in prereqs:
                        current_pr_level = self.skill_proficiency[pr]
                        if current_pr_level < boost_level:
                            self.skill_proficiency[pr] = min(boost_level, current_pr_level + 0.2)
                            self.skill_consistency[pr] = min(1.0, self.skill_consistency[pr] + 0.15)
                            boost_prerequisites(pr, boost_level * 0.95)
                boost_prerequisites(skill_id)

                # --- Boost nodos intermedios ---
                for node in node_ids:
                    if node in self.dominated_nodes:
                        continue
                    prereqs = prerequisites.get(node, [])
                    successors = [e['target'] for e in edges if e['source'] == node]
                    if any(p in self.dominated_nodes for p in prereqs) and any(s in self.dominated_nodes for s in successors):
                        self.skill_proficiency[node] = min(1.0, max(self.skill_proficiency[node], 0.7 + 0.3*random.random()))
                        self.skill_consistency[node] = min(1.0, self.skill_consistency[node] + 0.2)

            self.consecutive_successes[skill_id] += 1
            self.frustration_level = max(0, self.frustration_level - 1)

        else:
            base_penalty = 0.15 * (1.0 - self.skill_consistency[skill_id])
            failed_penalty = 0.1 * (self.failed_attempts[skill_id] + 1)
            total_penalty = base_penalty + failed_penalty
            self.skill_proficiency[skill_id] = max(-0.3, current_level - total_penalty)
            self.skill_consistency[skill_id] *= 0.5
            if skill_id in self.dominated_nodes and self.skill_proficiency[skill_id] < 0.7:
                self.dominated_nodes.remove(skill_id)

        # Actualizar historial y tiempo
        self.elapsed_time_on_skills[skill_id] = self.elapsed_time_on_skills.get(skill_id, 0) + outcome["time_spent"]
        self.path_history.append(skill_id)

    def choose_action(self):
        available_skills = [
            n for n in node_ids
            if self.skill_proficiency[n] < 1.0
            and all(self.skill_proficiency.get(p, 0.0) >= 0.5 for p in get_all_prerequisites(n, prerequisites))
        ]
        if not available_skills:
            return random.choice(list(node_ids))
        return random.choice(available_skills)

# --- Simulación de outcomes ---
def simulate_outcome(skill_id, student):
    all_prereqs = get_all_prerequisites(skill_id, prerequisites)
    current_level = student.skill_proficiency[skill_id]
    current_mastery = student.skill_mastery[skill_id]

    consistency_bonus = student.skill_consistency[skill_id] * 0.3
    dominated_bonus = 0.2 if skill_id in student.dominated_nodes else 0.0

    base_success = 0.45 + (0.35 * current_level) + consistency_bonus + dominated_bonus
    if skill_id in student.dominated_nodes and all(student.skill_proficiency[p] > 0.7 for p in all_prereqs):
        base_success = min(0.95, base_success + 0.3)

    fatigue_factor = max(0.4, 1 - 0.2 * student.frustration_level)
    prereq_factor = 1.0  # Se elimina prereq_penalty indefinido

    success_prob = min(0.95, max(0.15, base_success * fatigue_factor * prereq_factor))
    success = random.random() < success_prob

    if success:
        score_base = 0.75 + 0.2 * current_level
        score = round(random.uniform(score_base, 0.98), 2)
        time_spent = int(max(10, random.gauss(150 + 100 * (1 - current_level) * (1 - current_mastery), 20)))
    else:
        score_base = 0.15 + 0.1 * current_level
        score = round(random.uniform(score_base, 0.45), 2)
        time_spent = int(max(10, random.gauss(250 + 150 * (1 - current_level), 35)))

    return {"success": success, "score": score, "time_spent": time_spent}

# --- Recompensas ---
def calculate_reward(outcome, current_proficiency, total_mastery=0.0):
    if outcome["success"]:
        reward = 0.7 + 1.2 * (1.0 - current_proficiency)
        reward += 0.3 * total_mastery
        return min(reward, 2.5)
    else:
        return -0.7

# --- Generación de datos sintéticos ---
def generate_synthetic_data():
    if not node_ids:
        print("No se encontraron nodos. Abortando la generación de datos.")
        return

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    
    with open(OUTPUT_PATH, 'w') as f:
        for i in range(TOTAL_STUDENTS):
            profile_type = "desde_cero" if i < TOTAL_STUDENTS / 3 else "parcial" if i < 2*TOTAL_STUDENTS/3 else "avanzado"
            student = SyntheticStudent(f"sint_{i:04d}", profile_type=profile_type)
            session_counter = 0

            for j in range(MAX_STEPS_PER_STUDENT):
                if j % STEPS_PER_SESSION == 0:
                    session_counter += 1
                    student.reset_session_tracking()

                mastered_nodes = sum(1 for n in node_ids if student.skill_proficiency[n] >= MASTERY_THRESHOLD)
                if mastered_nodes >= len(node_ids) * MAX_SIMULATION_MASTERY:
                    break

                current_state = student.get_state()
                recommended_skill = student.choose_action()
                outcome = simulate_outcome(recommended_skill, student)
                total_mastery = sum(student.skill_proficiency.values()) / len(node_ids)
                reward = calculate_reward(outcome, current_state["skill_proficiency"].get(recommended_skill, 0.0), total_mastery)
                student.update_state(recommended_skill, outcome)

                f.write(json.dumps({
                    "student_id": student.student_id,
                    "profile_type": student.profile_type,
                    "step_number": j + 1,
                    "session_id": f"ses_{student.student_id}_{session_counter}",
                    "state": current_state,
                    "action": {"recommended_skill_id": recommended_skill},
                    "outcome": outcome,
                    "reward": reward
                }) + "\n")
                
    print(f"Datos sintéticos generados en {OUTPUT_PATH}. Total de {TOTAL_STUDENTS} estudiantes simulados.")

if __name__ == "__main__":
    generate_synthetic_data()
