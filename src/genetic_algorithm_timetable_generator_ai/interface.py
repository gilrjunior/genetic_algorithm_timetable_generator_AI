import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import os
import numpy as np
from GeneticAlgorithm import GeneticAlgorithm
from mock_data import subjects  # Importa aqui para evitar import circular

class Interface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gerador de Grade Horária - Algoritmo Genético")
        self.root.geometry("1800x1000")
        self.root.configure(bg="#F0F0F0")

        # Flag para indicar se está executando
        self.is_running = False
        self.stop_flag = False
        self.ga = None
        self.best_generation = 0
        self.best_timetable = None

        self.setup_styles()
        self.create_frames()
        self.create_controls()
        self.create_graphs()
        self.create_timetable_view()

        # Labels para mostrar informações em tempo real (em uma linha)
        self.status_frame = ttk.Frame(self.frame_controls, style="TFrame")
        self.status_frame.grid(row=12, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        self.generation_label = ttk.Label(self.status_frame, text="Geração Atual: 0", style="TLabel")
        self.generation_label.pack(side="left", padx=(0, 10))
        self.best_generation_label = ttk.Label(self.status_frame, text="Melhor Geração: 0", style="TLabel")
        self.best_generation_label.pack(side="left", padx=(0, 10))
        self.best_fitness_label = ttk.Label(self.status_frame, text="Melhor Aptidão: 0", style="TLabel")
        self.best_fitness_label.pack(side="left")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#F0F0F0")
        style.configure("TLabel", background="#F0F0F0", foreground="#333333", font=("Arial", 10))
        style.configure("Rounded.TEntry",
                        fieldbackground="white",
                        bordercolor="#CCCCCC",
                        lightcolor="#CCCCCC",
                        foreground="#000000",
                        padding=3,
                        borderwidth=1,
                        relief="solid")
        style.configure("Red.TButton",
                        foreground="white",
                        background="#FF0000",
                        padding=3,
                        borderwidth=1,
                        relief="solid",
                        anchor="center")
        style.map("Red.TButton",
            foreground=[("active", "black")],
            background=[("active", "white")]
        )
        style.configure("Treeview", 
                        background="white",
                        foreground="black",
                        rowheight=36,
                        font=("Arial", 9),
                        fieldbackground="white")
        style.configure("Treeview.Heading",
                        background="#CCCCCC",
                        foreground="black",
                        font=("Arial", 9, "bold"),
                        relief="flat")
        style.map("Treeview.Heading",
            background=[("active", "#999999")])

    def create_frames(self):
        # Frame de controles (esquerda, mais compacto)
        self.frame_controls = ttk.Frame(self.root, padding=5, style="TFrame")
        self.frame_controls.grid(row=0, column=0, rowspan=2, sticky="nsw", padx=5, pady=5)

        # Frame do gráfico (direita, topo, menor)
        self.frame_graph = ttk.Frame(self.root, padding=5, style="TFrame")
        self.frame_graph.grid(row=0, column=1, sticky="new", padx=5, pady=(5, 2))

        # Frame da tabela de horário (abaixo do gráfico, ocupando toda a largura)
        self.frame_timetable = ttk.Frame(self.root, padding=5, style="TFrame")
        self.frame_timetable.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=(2, 5))

        # Configuração das linhas e colunas
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=2)
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)

    def create_timetable_view(self):
        dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
        horarios = [
            "19h00 à 19h50",
            "19h50 à 20h40",
            "20h50 à 21h40",
            "21h40 à 22h30"
        ]
        periods = [f"Período {i+1}" for i in range(6)]
        columns = periods
        self.timetable_tree = ttk.Treeview(self.frame_timetable, height=20)
        self.timetable_tree["columns"] = columns
        self.timetable_tree.column("#0", width=180, minwidth=180, anchor="w")
        for col in columns:
            self.timetable_tree.column(col, width=140, minwidth=100, anchor="w")
            self.timetable_tree.heading(col, text=col)
        # Limpa linhas antigas se houver
        for item in self.timetable_tree.get_children():
            self.timetable_tree.delete(item)
        # Adiciona scrollbars
        scrollbar_y = ttk.Scrollbar(self.frame_timetable, orient="vertical", command=self.timetable_tree.yview)
        scrollbar_x = ttk.Scrollbar(self.frame_timetable, orient="horizontal", command=self.timetable_tree.xview)
        self.timetable_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        self.timetable_tree.pack(side="left", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")

    def update_timetable(self, timetable):
        if timetable is None:
            return

        from mock_data import subjects

        # Limpa a tabela atual
        for item in self.timetable_tree.get_children():
            self.timetable_tree.delete(item)

        dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
        horarios = [
            "19h00 à 19h50",
            "19h50 à 20h40",
            "20h50 à 21h40",
            "21h40 à 22h30"
        ]
        # Configura zebra striping e borda cinza fina
        self.timetable_tree.tag_configure('evenrow', background='#f0f0f0')
        self.timetable_tree.tag_configure('oddrow', background='#ffffff')
        self.timetable_tree.tag_configure('dayborder', background='#b0b0b0')
        row_index = 0
        # Para cada dia e slot (linha)
        for day in range(len(dias)):
            if day > 0:
                # Insere uma linha cinza fina para separar os dias
                self.timetable_tree.insert("", "end", text="", values=["" for _ in range(6)], tags=('dayborder',))
                row_index += 1
            for slot in range(len(horarios)):
                row_label = f"{dias[day]} - {horarios[slot]}"
                values = []
                for period in range(6):
                    subject_id = timetable.get_subject_at(period, day, slot)
                    if subject_id == 0:
                        values.append("Vazio")
                    else:
                        subject = next((s for s in subjects if s.id == subject_id), None)
                        if subject:
                            values.append(f"{subject.name}\n{subject.teacher}")
                        else:
                            values.append(f"ID {subject_id}")
                tag = 'evenrow' if row_index % 2 == 0 else 'oddrow'
                self.timetable_tree.insert("", "end", text=row_label, values=values, tags=(tag,))
                row_index += 1

    def create_graphs(self):
        # Gráfico da aptidão (menor)
        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.ax.set_title("Evolução da Aptidão")
        self.ax.set_xlabel("Geração")
        self.ax.set_ylabel("Aptidão")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_graph)
        self.canvas.get_tk_widget().pack()

        # Lista para armazenar os dados do gráfico
        self.generations = []
        self.fitness_values = []

    def update_display(self, generation, best_individual, best_fitness):
        # Atualiza as labels
        self.generation_label.config(text=f"Geração Atual: {generation}")

        # Mantém a exibição da melhor aptidão e da geração em que ela foi encontrada
        if best_fitness > getattr(self, 'best_fitness', float('-inf')):
            self.best_fitness = best_fitness
            self.best_generation = generation
            self.best_timetable = best_individual
            self.best_generation_label.config(text=f"Melhor Geração: {generation}")
            self.best_fitness_label.config(text=f"Melhor Aptidão: {best_fitness:.4f}")
            # Atualiza a tabela de horário
            self.update_timetable(best_individual)
        else:
            # Garante que os labels continuam visíveis mesmo se não houver atualização
            self.best_generation_label.config(text=f"Melhor Geração: {getattr(self, 'best_generation', 0)}")
            self.best_fitness_label.config(text=f"Melhor Aptidão: {getattr(self, 'best_fitness', 0):.4f}")

        # Atualiza o gráfico
        self.generations.append(generation)
        self.fitness_values.append(best_fitness)
        self.ax.clear()
        self.ax.set_title("Evolução da Aptidão")
        self.ax.set_xlabel("Geração")
        self.ax.set_ylabel("Aptidão")
        self.ax.plot(self.generations, self.fitness_values, 'b-')
        self.ax.grid(True)
        self.canvas.draw()
        self.root.update_idletasks()

    def start_algorithm(self):
        if self.is_running:
            return
        
        self.is_running = True
        self.stop_flag = False
        self.best_fitness = float('-inf')
        self.generations = []
        self.fitness_values = []
        
        # Lê os parâmetros
        population_size = int(self.entries["Tamanho da População:"].get())
        crossover_prob = float(self.entries["Probabilidade de Cruzamento:"].get())
        mutation_prob = float(self.entries["Probabilidade de Mutação:"].get())
        generations = int(self.entries["Número de Gerações:"].get())
        elitism_size = int(self.entries["Tamanho do Elitismo:"].get())
        tournament_size = int(self.tournament_size.get())
        selection_method = self.selection_method.get()

        # Cria a instância do algoritmo genético
        self.ga = GeneticAlgorithm(
            population_size=population_size,
            crossover_rate=crossover_prob,
            mutation_rate=mutation_prob,
            elitism_count=elitism_size,
            tournament_size=tournament_size,
            selection_method=selection_method
        )

        # Configura o callback de parada
        self.ga.stop = lambda: self.stop_flag

        # Inicia o algoritmo em uma thread separada
        self.algorithm_thread = threading.Thread(
            target=self.ga.run,
            args=(generations, self.update_display),
            daemon=True
        )
        self.algorithm_thread.start()

    def create_controls(self):
        # Parâmetros do AG
        labels_and_defaults = [
            ("Tamanho da População:", "100"),
            ("Probabilidade de Cruzamento:", "0.85"),
            ("Probabilidade de Mutação:", "0.2"),
            ("Número de Gerações:", "100"),
            ("Tamanho do Elitismo:", "2")
        ]

        self.entries = {}
        for idx, (text, default_value) in enumerate(labels_and_defaults):
            lbl = ttk.Label(self.frame_controls, text=text, style="TLabel")
            lbl.grid(row=idx, column=0, padx=5, pady=5, sticky="w")

            entry = ttk.Entry(self.frame_controls, style="Rounded.TEntry", width=25)
            entry.grid(row=idx, column=1, padx=5, pady=5, sticky="w")
            entry.insert(0, default_value)
            self.entries[text] = entry

        # Método de Seleção
        self.selection_method = tk.StringVar(value="roulette")
        ttk.Label(self.frame_controls, text="Método de Seleção:", style="TLabel").grid(row=6, column=0, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(self.frame_controls, text="Roleta", variable=self.selection_method, value="roulette").grid(row=6, column=1, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(self.frame_controls, text="Torneio", variable=self.selection_method, value="tournament").grid(row=7, column=1, padx=5, pady=5, sticky="w")

        # Tamanho do Torneio
        ttk.Label(self.frame_controls, text="Tamanho do Torneio:", style="TLabel").grid(row=8, column=0, padx=5, pady=5, sticky="w")
        self.tournament_size = ttk.Entry(self.frame_controls, style="Rounded.TEntry", width=25)
        self.tournament_size.grid(row=8, column=1, padx=5, pady=5, sticky="w")
        self.tournament_size.insert(0, "3")

        # Botões de Controle
        btn_start = ttk.Button(
            self.frame_controls,
            text="Iniciar",
            style="Red.TButton",
            command=self.start_algorithm
        )
        btn_start.grid(row=11, column=0, padx=5, pady=10, sticky="w")

        btn_stop = ttk.Button(
            self.frame_controls,
            text="Parar",
            style="Red.TButton",
            command=self.stop_algorithm
        )
        btn_stop.grid(row=11, column=1, padx=5, pady=10, sticky="w")

    def stop_algorithm(self):
        self.stop_flag = True
        self.is_running = False

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        self.stop_flag = True
        if hasattr(self, "algorithm_thread") and self.algorithm_thread.is_alive():
            self.algorithm_thread.join(timeout=2)
        self.root.destroy()
        os._exit(0)