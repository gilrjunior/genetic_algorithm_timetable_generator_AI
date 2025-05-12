import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import os
import numpy as np
from GeneticAlgorithm import GeneticAlgorithm

class Interface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Genetic Algorithm Function Maximizer")
        self.root.geometry("1300x900")
        self.root.configure(bg="#F0F0F0")

        # Flag para indicar se está executando
        self.is_running = False
        self.stop_flag = False
        self.ga = None

        self.setup_styles()
        self.create_frames()
        self.create_controls()
        self.create_graphs()

        # Labels para mostrar informações em tempo real
        self.generation_label = ttk.Label(self.frame_controls, text="Geração: 0", style="TLabel")
        self.generation_label.grid(row=12, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        self.best_fitness_label = ttk.Label(self.frame_controls, text="Melhor Aptidão: 0", style="TLabel")
        self.best_fitness_label.grid(row=13, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        self.best_individual_label = ttk.Label(self.frame_controls, text="Melhor Indivíduo: []", style="TLabel")
        self.best_individual_label.grid(row=14, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        self.error_label = ttk.Label(self.frame_controls, text="Erro: 0%", style="TLabel")
        self.error_label.grid(row=15, column=0, columnspan=2, padx=5, pady=5, sticky="w")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#F0F0F0")
        style.configure("TLabel", background="#F0F0F0", foreground="#333333", font=("Arial", 12))
        style.configure("Rounded.TEntry",
                        fieldbackground="white",
                        bordercolor="#CCCCCC",
                        lightcolor="#CCCCCC",
                        foreground="#000000",
                        padding=5,
                        borderwidth=2,
                        relief="solid")
        style.configure("Red.TButton",
                        foreground="white",
                        background="#FF0000",
                        padding=5,
                        borderwidth=2,
                        relief="solid",
                        anchor="center")
        style.map("Red.TButton",
            foreground=[("active", "black")],
            background=[("active", "white")]
        )

    def create_frames(self):
        self.frame_controls = ttk.Frame(self.root, padding=10, style="TFrame")
        self.frame_controls.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

        self.frame_graph = ttk.Frame(self.root, padding=10, style="TFrame")
        self.frame_graph.grid(row=0, column=1, sticky="ne", padx=10, pady=10)

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

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

        # Tipo de Cruzamento
        self.crossover_type = tk.StringVar(value="single_point")
        ttk.Label(self.frame_controls, text="Tipo de Cruzamento:", style="TLabel").grid(row=9, column=0, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(self.frame_controls, text="Um Ponto", variable=self.crossover_type, value="single_point").grid(row=9, column=1, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(self.frame_controls, text="Dois Pontos", variable=self.crossover_type, value="double_point").grid(row=10, column=1, padx=5, pady=5, sticky="w")

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

    def create_graphs(self):
        # Gráfico da função
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.ax.set_title("Função e Melhor Indivíduo")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_graph)
        self.canvas.get_tk_widget().pack()

    def start_algorithm(self):

        if self.is_running:
            return
        
        self.is_running = True
        self.stop_flag = False
        
        # Lê os parâmetros
        population_size = int(self.entries["Tamanho da População:"].get())
        crossover_prob = float(self.entries["Probabilidade de Cruzamento:"].get())
        mutation_prob = float(self.entries["Probabilidade de Mutação:"].get())
        generations = int(self.entries["Número de Gerações:"].get())
        elitism_size = int(self.entries["Tamanho do Elitismo:"].get())
        tournament_size = int(self.tournament_size.get())
        selection_method = self.selection_method.get()
        crossover_type = self.crossover_type.get()

        # Cria a instância do algoritmo genético
        self.ga = GeneticAlgorithm(
            population_size=population_size,
            crossover_rate=crossover_prob,
            mutation_rate=mutation_prob,
            elitism_count=elitism_size,
            tournament_size=tournament_size,
            selection_method=selection_method,
            crossover_type=crossover_type,
            decimal_precision=4,
        )

        # Configura o callback de parada
        self.ga.stop = lambda: self.stop_flag

        # Inicia o algoritmo em uma thread separada
        self.algorithm_thread = threading.Thread(
            target=self.ga.run,
            args=(generations,self.update_display),
            daemon=True
        )
        self.algorithm_thread.start()

    def stop_algorithm(self):
        self.stop_flag = True
        self.is_running = False

    def update_display(self, generation, best_individual, best_fitness, error):
        """Atualiza a interface com os resultados do algoritmo"""
        self.generation_label.config(text=f"Geração: {generation}")
        self.best_fitness_label.config(text=f"Melhor Aptidão: {best_fitness:.4f}")
        self.best_individual_label.config(text=f"Melhor Indivíduo: {best_individual}")
        self.error_label.config(text=f"Erro: {error:.2f}%")

        # Atualiza o gráfico
        self.ax.clear()
        self.ax.set_title("Função e Melhor Indivíduo")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        
        # Plota a função de Rastrigin
        x = np.linspace(-3.1, 12.1, 200)
        y = np.linspace(4.1, 5.8, 200)
        X, Y = np.meshgrid(x, y)
        Z = 20 + (X**2 - 10*np.cos(2*np.pi*X)) + (Y**2 - 10*np.cos(2*np.pi*Y))
        
        # Plota a superfície
        self.ax.contourf(X, Y, Z, levels=20, cmap='viridis')
        
        # Plota o melhor indivíduo
        if best_individual is not None and len(best_individual) >= 2:
            self.ax.plot(best_individual[0], best_individual[1], 'ro', markersize=10, label='Melhor Indivíduo')
            self.ax.legend()
        
        self.canvas.draw()
        
        # Atualiza a interface
        self.root.update_idletasks()

    def on_closing(self):
        self.stop_flag = True
        if hasattr(self, "algorithm_thread") and self.algorithm_thread.is_alive():
            self.algorithm_thread.join(timeout=2)
        self.root.destroy()
        os._exit(0)

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()