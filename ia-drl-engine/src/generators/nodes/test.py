import tkinter as tk
from tkinter import ttk, messagebox
import node_1a

def generar():
    # Obtener valores seleccionados
    dificultad = int(combo_dificultad.get())
    tipo = combo_tipo.get().lower()

    # Llamar función correcta
    if tipo == "teorico":
        ejercicio = node_1a._generate_1a_theory(dificultad)
    elif tipo == "practico":
        ejercicio = node_1a._generate_1a_practical(dificultad)
    elif tipo == "dictado":
        ejercicio = node_1a._generate_1a_dictation(dificultad)
    else:
        messagebox.showerror("Error", "Selecciona un tipo válido.")
        return

    # Mostrar ejercicio y respuesta en la interfaz
    txt_output.delete("1.0", tk.END)
    txt_output.insert(tk.END, f"--- Ejercicio ---\n{ejercicio['exercise']}\n\n")
    
    if ejercicio["type"] == "practico":
        txt_output.insert(tk.END, f"Patrón rítmico: {ejercicio['rhythm_sequence']}\n")
    elif ejercicio["type"] == "dictado":
        txt_output.insert(tk.END, f"Audio: {ejercicio['audio_source']}\n")
    
    txt_output.insert(tk.END, f"\n--- Respuesta esperada ---\n{ejercicio['expected_answer']}\n")


# ----------------------------
#   Interfaz con Tkinter
# ----------------------------
root = tk.Tk()
root.title("Tester Nodo 1A - Ritmo (4/4)")
root.geometry("600x400")

# Selección dificultad
lbl_dif = tk.Label(root, text="Dificultad (1-3):")
lbl_dif.pack(pady=5)
combo_dificultad = ttk.Combobox(root, values=["1", "2", "3"])
combo_dificultad.current(0)
combo_dificultad.pack(pady=5)

# Selección tipo
lbl_tipo = tk.Label(root, text="Tipo de ejercicio:")
lbl_tipo.pack(pady=5)
combo_tipo = ttk.Combobox(root, values=["Teorico", "Practico", "Dictado"])
combo_tipo.current(0)
combo_tipo.pack(pady=5)

# Botón
btn = tk.Button(root, text="Generar Ejercicio", command=generar)
btn.pack(pady=10)

# Área de salida
txt_output = tk.Text(root, wrap="word", height=15, width=70)
txt_output.pack(pady=10)

root.mainloop()
