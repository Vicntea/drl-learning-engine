import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from dotenv import load_dotenv

from ia_drl_engine.src.utils.path_utils import resolve_path

from ia_drl_engine.src.utils.skill_mapping import load_skill_mapping

# ================================
# 📁 Cargar variables de entorno
# ================================
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../_envFiles/config.env"))


# ================================
# 📁 Rutas base
# ================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

dataset_path = resolve_path("@data/synthetic/ejemplo.jsonl")  # <-- cambia si es necesario
nodes_path = resolve_path("@data/graph/nodes.json")

model_dir = resolve_path("@models")
model_path = os.path.join(model_dir, "bc_model.pth")



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
print("Cargando dataset...")

data = []
with open(dataset_path) as f:
    for line in f:
        try:
            data.append(json.loads(line))
        except:
            continue  # ignora líneas corruptas

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

EPOCHS = 20
BATCH_SIZE = 64

print("Iniciando entrenamiento...")

for epoch in range(EPOCHS):

    perm = torch.randperm(X_tensor.size(0))

    total_loss = 0

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

    avg_loss = total_loss / (X_tensor.size(0) / BATCH_SIZE)

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