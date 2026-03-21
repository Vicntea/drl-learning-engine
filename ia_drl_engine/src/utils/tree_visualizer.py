import networkx as nx
import matplotlib.pyplot as plt
import json
import os
from collections import defaultdict

# Define las rutas de los archivos
GRAPH_PATH = '../../data/graph/nodes.json'
JSONL_PATH = '../../data/synthetic/synthetic_data.jsonl'
OUTPUT_DIR = '../../data/synthetic/learning_progress/' 

# Define el ID del estudiante que quieres visualizar
TARGET_STUDENT_ID = 'sint_0322'

# Carga el grafo desde el archivo JSON
def load_musical_tree(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

# Función para visualizar el árbol de progreso
def visualize_learning_path(session_data, all_nodes_data, filename):
    G = nx.DiGraph()
    
    # Añade todos los nodos al grafo para que se vean todos los conceptos
    for node in all_nodes_data['nodes']:
        G.add_node(node['id'], label=node['name'], level=node['level'])

    # Colores y estilos para el grafo
    node_colors = {}
    node_labels = {}
    
    # Asigna colores según el estado de la habilidad en la sesión
    for node in all_nodes_data['nodes']:
        skill_id = node['id']
        proficiency = session_data['state']['skill_proficiency'].get(skill_id, 0.0)
        
        if proficiency >= 0.9:
            node_colors[skill_id] = '#8FBC8F'  # Verde: Dominado
        elif proficiency > 0.0:
            node_colors[skill_id] = '#FFFFE0'  # Amarillo: En progreso
        elif proficiency == -1.0:
            node_colors[skill_id] = '#F08080'  # Rojo: Frustrado
        else:
            node_colors[skill_id] = '#D3D3D3'  # Gris: Pendiente

        node_labels[skill_id] = f"{node['name']}\n({proficiency:.2f})"

    # Añade las aristas del grafo
    for edge in all_nodes_data['edges']:
        G.add_edge(edge['source'], edge['target'])

    # Crea el layout del grafo por niveles
    pos = nx.multipartite_layout(G, subset_key='level', align='vertical')

    plt.figure(figsize=(15, 12))
    nx.draw(G, pos,
            node_color=[node_colors.get(node_id, '#D3D3D3') for node_id in G.nodes()],
            labels=node_labels,
            with_labels=True,
            node_size=2500,
            node_shape='o',
            font_size=8,
            font_weight='bold')
            
    plt.title(f"Progreso de Sesión {session_data['session_id']} - Paso {session_data.get('step_number', 'N/A')}")
    plt.savefig(filename)
    plt.close()

# Función para procesar la secuencia de eventos de una única sesión
def process_single_session(events, all_nodes_data, output_dir):
    if not events:
        return
    
    student_id = events[0]["student_id"]
    session_id = events[0]["session_id"]
    
    # Asegura que el directorio para las imágenes del estudiante y sesión exista
    student_output_dir = os.path.join(output_dir, student_id, session_id)
    os.makedirs(student_output_dir, exist_ok=True)
    
    # Itera sobre cada evento para generar una imagen por paso
    for i, event in enumerate(events):
        if 'state' in event:
            event['step_number'] = i + 1
            output_path = os.path.join(student_output_dir, f"step_{i+1:03d}.png")
            visualize_learning_path(event, all_nodes_data, output_path)
            print(f"Árbol de progreso guardado en: {output_path}")

# Función para procesar todas las sesiones de un estudiante específico
def process_student_sessions(jsonl_path, student_id, all_nodes_data, output_dir):
    sessions_by_student = defaultdict(list)
    
    try:
        with open(jsonl_path, 'r') as f:
            for line in f:
                event = json.loads(line)
                if event.get("student_id") == student_id:
                    session_id = event.get("session_id")
                    sessions_by_student[session_id].append(event)
    except FileNotFoundError:
        print(f"Error: El archivo {jsonl_path} no se encuentra.")
        return
    except json.JSONDecodeError:
        print(f"Error: El archivo {jsonl_path} tiene un formato JSONL inválido.")
        return

    if not sessions_by_student:
        print(f"No se encontraron datos para el estudiante {student_id}.")
        return

    # Procesa cada sesión del estudiante
    print(f"Procesando todas las sesiones del estudiante: {student_id}")
    for session_id, events in sessions_by_student.items():
        print(f"  > Procesando sesión: {session_id}")
        process_single_session(events, all_nodes_data, output_dir)
            
# Ejemplo de uso:
if __name__ == '__main__':
    all_nodes_data = load_musical_tree(GRAPH_PATH)
    process_student_sessions(JSONL_PATH, TARGET_STUDENT_ID, all_nodes_data, OUTPUT_DIR)