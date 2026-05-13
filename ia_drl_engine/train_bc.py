import os
import json
import csv
import torch
import torch.nn as nn
import torch.optim as optim
import argparse
from dotenv import load_dotenv

from ia_drl_engine.src.utils.path_utils import resolve_path

from ia_drl_engine.src.utils.skill_mapping import load_skill_mapping

# ================================
# 📁 Cargar variables de entorno
# ================================
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../_envFiles/config.env"))


# ================================
# 📁 Args y rutas base
# ================================
parser = argparse.ArgumentParser(description='Train a behavioral cloning (BC) model from CSV or JSONL dataset')
parser.add_argument('--dataset', default='@data/synthetic/ejemplo.jsonl', help='CSV or JSONL dataset path')
parser.add_argument('--model-out', default='@models/bc_model.pth', help='Path to save trained model')
parser.add_argument('--epochs', type=int, default=20)
parser.add_argument('--batch-size', type=int, default=64)
parser.add_argument('--lr', type=float, default=1e-3)
parser.add_argument('--clamp', action='store_true', help='Clamp skill proficiencies to [0,1] when reading CSV')
parser.add_argument('--compact', action='store_true', help='Treat CSV as compact (skills_compact column)')

args = parser.parse_args()

dataset_path = resolve_path(args.dataset)
nodes_path = resolve_path("@data/graph/nodes.json")

model_dir = resolve_path(os.path.dirname(args.model_out))
model_path = resolve_path(args.model_out)


skill_to_idx, idx_to_skill, ordered_skills = load_skill_mapping()

# ================================
# 🔄 State → Vector
# ================================
def state_to_vector(state):
    vec = []

    # Orden consistente
    for skill in ordered_skills:
        vec.append(state["skill_proficiency"].get(skill, 0))

    # Feature adicional
    vec.append(state.get("frustration_level", 0))

    return vec


# ================================
# 📥 Cargar dataset
# ================================
print("Cargando dataset JSONL...")

data = []
def load_from_csv(path, clamp=False, compact=False):
    rows = []
    with open(path, encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if not any(row):
                continue
            d = dict(zip(header, row))

            # build entry similar to JSONL
            # extract fixed
            student_id = d.get('student_id')
            profile_type = d.get('profile_type')
            step_number = int(d.get('step_number') or 0)
            session_id = d.get('session_id')
            recommended = d.get('recommended_skill_id')

            # outcome
            try:
                success = bool(int(d.get('outcome_success')))
            except Exception:
                success = d.get('outcome_success') in ['True', 'true', '1']

            try:
                score = float(d.get('outcome_score') or 0.0)
            except Exception:
                score = 0.0

            try:
                time_spent = int(float(d.get('outcome_time_spent') or 0))
            except Exception:
                time_spent = 0

            try:
                reward = float(d.get('reward') or 0.0)
            except Exception:
                reward = 0.0

            # skill proficiencies
            # if compact
            skill_proficiency = {}
            if compact and 'skills_compact' in header:
                compact_str = d.get('skills_compact') or ''
                _, _, ordered = load_skill_mapping()
                chunks = [compact_str[i:i+3] for i in range(0, len(compact_str), 3)]
                for s, ch in zip(ordered, chunks):
                    try:
                        val = int(ch)
                    except Exception:
                        val = 0
                    v = val / 100.0
                    if clamp:
                        v = max(0.0, min(1.0, v))
                    skill_proficiency[s] = v
            else:
                # use skill columns (all columns not fixed)
                fixed = ['student_id','profile_type','step_number','session_id','recommended_skill_id','outcome_success','outcome_score','outcome_time_spent','reward']
                skill_cols = [c for c in header if c not in fixed]
                for s in skill_cols:
                    raw = d.get(s,'')
                    try:
                        val = float(raw)
                    except Exception:
                        val = 0.0
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
                'state': {'skill_proficiency': skill_proficiency, 'frustration_level': 0},
                'action': {'recommended_skill_id': recommended},
                'outcome': {'success': success, 'score': score, 'time_spent': time_spent},
                'reward': reward
            }

            rows.append(entry)
    return rows


if dataset_path.lower().endswith('.csv'):
    data = load_from_csv(dataset_path, clamp=getattr(args,'clamp',False), compact=getattr(args,'compact',False))
else:
    with open(dataset_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data.append(json.loads(line))
            except Exception:
                continue

print(f"Total muestras: {len(data)}")


# ================================
# 🧱 Construir X e y
# ================================
X = []
y = []

for step in data:
    state = step.get("state", {})
    action = step.get("action", {}).get("recommended_skill_id")

    if not state or not action:
        continue

    if action not in skill_to_idx:
        continue

    try:
        X.append(state_to_vector(state))
        y.append(skill_to_idx[action])
    except:
        continue


print(f"Datos válidos: {len(X)}")


# ================================
# 🔢 Tensores
# ================================
X_tensor = torch.tensor(X, dtype=torch.float32)
y_tensor = torch.tensor(y, dtype=torch.long)


# ================================
# 🤖 Modelo BC
# ================================
class BCModel(nn.Module):
    def __init__(self, input_dim, output_dim):
        super().__init__()

        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, output_dim)
        )

    def forward(self, x):
        return self.net(x)


model = BCModel(
    input_dim=X_tensor.shape[1],
    output_dim=len(skill_to_idx)
)


# ================================
# ⚙️ Entrenamiento
# ================================
optimizer = optim.Adam(model.parameters(), lr=1e-3)
criterion = nn.CrossEntropyLoss()


EPOCHS = args.epochs
BATCH_SIZE = args.batch_size

print("Iniciando entrenamiento...")

for epoch in range(EPOCHS):

    perm = torch.randperm(X_tensor.size(0))

    total_loss = 0.0

    for i in range(0, X_tensor.size(0), BATCH_SIZE):
        indices = perm[i:i+BATCH_SIZE]

        batch_x = X_tensor[indices]
        batch_y = y_tensor[indices]

        logits = model(batch_x)
        loss = criterion(logits, batch_y)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    avg_loss = total_loss / max(1, (X_tensor.size(0) / BATCH_SIZE))

    print(f"Epoch {epoch+1}/{EPOCHS} - Loss: {avg_loss:.4f}")

# ================================
# 💾 Guardar modelo
# ================================
os.makedirs(model_dir, exist_ok=True)

torch.save({
    "model_state_dict": model.state_dict(),
    "skill_to_idx": skill_to_idx,
    "idx_to_skill": idx_to_skill,
}, model_path)

print(f"Modelo BC guardado en: {model_path}")