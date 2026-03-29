import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# CLEAN SEQUENCE FUNCTION
# -----------------------------
def clean_sequence(seq):
    seq = seq.upper()
    cleaned = "".join([c for c in seq if c in "ATGC"])
    return cleaned

# -----------------------------
# Placeholder hybrid model function
# -----------------------------
def predict_sequence(sequence):
    class_type = np.random.choice(['normal', 'moderate', 'diseased'])
    probability = np.random.rand()
    predicted_disease_index = np.random.randint(0,7)
    return class_type, probability, predicted_disease_index

# -----------------------------
# Risk Score Functions
# -----------------------------
def map_probability_to_risk(prob, class_type):
    if class_type == "normal":
        return 1 + prob*29
    elif class_type == "moderate":
        return 31 + prob*29
    else:
        return 61 + prob*39

def risk_category(score):
    if 1 <= score <= 15:
        return "Low Normal"
    elif 16 <= score <= 30:
        return "High Normal"
    elif 31 <= score <= 45:
        return "Low Moderate"
    elif 46 <= score <= 60:
        return "High Moderate"
    elif 61 <= score <= 80:
        return "Low Diseased"
    elif 81 <= score <= 100:
        return "High Diseased"

# -----------------------------
# Disease & Gene Mapping
# -----------------------------
disease_list = ["Diabetes", "Cancer", "Alzheimer", "Heart Disease", "Parkinson", "Hepatitis", "Malaria"]
gene_dict = {
    "Diabetes": "INS",
    "Cancer": "BRCA1",
    "Alzheimer": "APP",
    "Heart Disease": "MYH7",
    "Parkinson": "SNCA",
    "Hepatitis": "HCV",
    "Malaria": "PfEMP1",
}

# -----------------------------
# GC / AT PIE CHART
# -----------------------------
def plot_gc_at_pie(sequence):
    sequence = sequence.upper()
    gc_count = sequence.count('G') + sequence.count('C')
    at_count = sequence.count('A') + sequence.count('T')
    labels = ['GC', 'AT']
    sizes = [gc_count, at_count]
    colors = ['#2ca02c', '#ff7f0e']
    plt.figure(figsize=(5,5))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, textprops={'fontsize':12})
    plt.title("GC vs AT Content", fontsize=14, fontweight='bold')
    plt.show()

# -----------------------------
# MODEL PERFORMANCE BAR CHART
# -----------------------------
def plot_model_performance():
    model_names = ['Logistic', 'SVM', 'RF', 'XGBoost', '1D-CNN', 'Hybrid']
    accuracies = [75, 77.38, 77.38, 88.10, 91.67, 94.05]
    plt.figure(figsize=(8,5))
    plt.bar(model_names, accuracies)
    plt.ylim(0,100)
    plt.ylabel("Accuracy (%)")
    plt.title("Model Performance Comparison")
    for i,v in enumerate(accuracies):
        plt.text(i, v+1, f"{v}%", ha='center')
    plt.show()

# -----------------------------
# LOAD FASTA / FNA / TXT FILES
# -----------------------------
sequences = []
predictions = []

def load_file():
    global sequences
    file_path = filedialog.askopenfilename(
        filetypes=[("Sequence Files", ".fasta .fa .fna .txt .seq .dna"), ("All files", "*.*")]
    )
    if not file_path:
        return

    try:
        sequences.clear()
        current_seq = ""

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()

                # FASTA header skip
                if line.startswith(">"):
                    if current_seq != "":
                        sequences.append(clean_sequence(current_seq))
                        current_seq = ""
                else:
                    current_seq += line

        # last sequence add
        if current_seq != "":
            sequences.append(clean_sequence(current_seq))

        sequences = [seq for seq in sequences if seq]

        if not sequences:
            messagebox.showwarning("Empty File", "No valid DNA sequences found.")
            return

        messagebox.showinfo("File Loaded", f"{len(sequences)} sequences loaded!")
        predict_all_sequences()

    except Exception as e:
        messagebox.showerror("File Error", f"Failed to load file:\n{e}")

# -----------------------------
# RUN PREDICTIONS
# -----------------------------
def predict_all_sequences():
    global predictions
    predictions.clear()

    for seq in sequences:
        class_type, prob, disease_idx = predict_sequence(seq)
        score = map_probability_to_risk(prob, class_type)
        category = risk_category(score)
        disease = disease_list[disease_idx]
        gene = gene_dict[disease]

        predictions.append([seq, f"{score:.2f}", category, disease, gene])

    filter_by_gene()

# -----------------------------
# GENE FILTER
# -----------------------------
def filter_by_gene(event=None):
    selected_gene = gene_filter_var.get()
    for row in tree.get_children():
        tree.delete(row)
    for pred in predictions:
        if selected_gene == "All Genes" or pred[4] == selected_gene:
            tree.insert('', 'end', values=pred)

# -----------------------------
# PIE CHART BUTTON
# -----------------------------
def show_pie_chart():
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("Select a Sequence", "Choose a sequence from the table.")
        return
    seq = tree.item(selected)['values'][0]
    plot_gc_at_pie(seq)

# -----------------------------
# GUI START
# -----------------------------
root = tk.Tk()
root.title("DNA Disease Risk Prediction - Final Year Project")
root.geometry("950x650")

# Buttons
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

tk.Button(btn_frame, text="Load File & Predict", command=load_file, width=25).grid(row=0, column=0, padx=5)
tk.Button(btn_frame, text="Show GC vs AT Pie Chart", command=show_pie_chart, width=25).grid(row=0, column=1, padx=5)
tk.Button(btn_frame, text="Show Model Performance", command=plot_model_performance, width=25).grid(row=0, column=2, padx=5)

# Gene filter dropdown
gene_filter_var = tk.StringVar()
gene_options = ["All Genes"] + list(gene_dict.values())
gene_filter_var.set("All Genes")

tk.Label(root, text="Filter by Gene").pack()
gene_dropdown = tk.OptionMenu(root, gene_filter_var, *gene_options, command=filter_by_gene)
gene_dropdown.pack(pady=5)

# Table
columns = ["Sequence","Risk Score","Risk Category","Disease","Gene"]
tree = ttk.Treeview(root, columns=columns, show='headings', height=20)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=160)

tree.pack(fill='both', expand=True)

scrollbar = ttk.Scrollbar(root, orient="vertical", command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side='right', fill='y')

root.mainloop()
