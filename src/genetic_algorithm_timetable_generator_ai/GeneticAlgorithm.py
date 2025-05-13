import numpy as np
import math
import random
from .subject import Subject

class GeneticAlgorithm:
    def __init__(self, population_size, mutation_rate, crossover_rate, elitism_count = None,
                 selection_method='roulette', tournament_size=None,):
        """
        Inicializa os parâmetros do algoritmo genético.

        :param population_size: Tamanho da população.
        :param mutation_rate: Taxa de mutação.
        :param crossover_rate: Taxa de cruzamento.
        :param elitism_count: Número de indivíduos a serem selecionados para a próxima geração.
        :param selection_method: Método de seleção (roulette ou tournament).
        :param tournament_size: Tamanho do torneio (se selection_method for tournament).
        :param crossover_type: Tipo de cruzamento (single_point ou double_point).
        :param max_known_value: Valor máximo conhecido da função, nem sempre é conhecido.
        """
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism_count = elitism_count
        self.selection_method = selection_method
        self.tournament_size = tournament_size
        self.best_individual = None
        self.best_fitness = None
        self.current_population = None
        self.stop = None # Callback para parar o algoritmo
        
        # Dimensões da grade horária
        self.num_periods = 6  # Número de períodos
        self.num_days = 5     # Número de dias na semana
        self.num_slots = 4    # Número de aulas por dia
        
        # Informações sobre as disciplinas e professores
        self.subjects = None  # Lista de disciplinas
        self.teachers = None  # Lista de professores
        self.subject_teachers = None  # Mapeamento de disciplinas para professores
        self.period_subjects = None   # Mapeamento de períodos para disciplinas

    def fitness_function(self):
        """
        Função real a ser maximizada.
        """

        ammount_conflicts = 0
        ammount_gaps = 0
        ammount_consecutive_classes = 0

        return 500 - 20 * ammount_conflicts - 5 * ammount_gaps + 10 * ammount_consecutive_classes

    def count_conflicts(self):
        """        
            Conta o número de conflitos entre os horários dos professores.
        """
        conflicts = 0

        return  conflicts

    def count_gaps(self):
        """
        Conta o número de gaps entre as aulas.
        """
        gaps = 0

        return  gaps

    def count_consecutive_classes(self):
        """
        Conta o número de aulas consecutivas.
        """
        
        consecutive_classes = 0

        return consecutive_classes

    def initialize_population(self):
        """
        Cria a população inicial de indivíduos.
        Cada indivíduo é uma matriz 2D representando a grade horária:
        - Linhas: Períodos (6)
        - Colunas: Slots totais (20 = 5 dias x 4 aulas)
        """
        if not all([self.subjects, self.period_subjects]):
            raise ValueError("As informações de disciplinas devem ser definidas antes de inicializar a população")

        population = []
        
        for _ in range(self.population_size):
            # Cria uma matriz vazia para cada indivíduo
            timetable = np.zeros((self.num_periods, self.num_slots), dtype=int)
            
            # Para cada período
            for period in range(self.num_periods):
                # Obtém as disciplinas deste período
                period_subjects = self.period_subjects[period]
                
                # Para cada disciplina do período
                for subject in period_subjects:
                    # Distribui as aulas da disciplina ao longo da semana
                    remaining_classes = 4  # Número de aulas por semana
                    
                    while remaining_classes > 0:
                        # Escolhe aleatoriamente um slot
                        slot = random.randint(0, self.num_slots - 1)
                        
                        # Se o slot estiver vazio
                        if timetable[period, slot] == 0:
                            # Atribui a disciplina
                            timetable[period, slot] = subject.id
                            remaining_classes -= 1
            
            population.append(timetable)
        
        return np.array(population)

    def _get_day_and_slot(self, slot_index):
        """
        Converte um índice de slot (0-19) em dia (0-4) e horário (0-3)
        """
        day = slot_index // 4
        time_slot = slot_index % 4
        return day, time_slot

    def _get_slot_index(self, day, time_slot):
        """
        Converte dia (0-4) e horário (0-3) em índice de slot (0-19)
        """
        return day * 4 + time_slot

    def fitness(self):
        """
        Calcula a aptidão (fitness) da população.
        Atualiza o melhor indivíduo, o erro do melhor e o erro médio da população.
        """
        fitness_values = self.fitness_function()
        # Índice do melhor indivíduo
        best_idx = np.argmax(fitness_values)
        self.best_individual = self.current_population[best_idx]
        self.best_fitness = fitness_values[best_idx]

        return fitness_values


    def selection(self, fitness_values):
        """
        Seleciona os indivíduos para reprodução, com base no método definido.
        """

        # Seleciona o método de seleção
        if self.selection_method == 'roulette':
            # Seleciona os indivíduos para reprodução
            self.current_population = self.roulette_selection(fitness_values)
        elif self.selection_method == 'tournament':
            # Seleciona os indivíduos para reprodução
            self.current_population = self.tournament_selection(fitness_values)

    def roulette_selection(self, fitness_values):
        """
        Implementa a seleção por roleta.
        """

        # Calcula a probabilidade de cada indivíduo
        probabilities = fitness_values / np.sum(fitness_values)
        # Seleciona os indivíduos para reprodução
        selected_individuals = np.random.choice(len(self.current_population), size=self.population_size, p=probabilities)
        # Retorna os indivíduos selecionados
        return self.current_population[selected_individuals]

    def tournament_selection(self, fitness_values):
        """
        Implementa a seleção por torneio.
        """
        selected = []

        for _ in range(self.population_size):
            # Sorteia os indivíduos aleatórios da população de acordo com o tamanho do torneio
            participants_indices = np.random.choice(len(self.current_population), self.tournament_size, replace=False)
            participants_fitness = fitness_values[participants_indices]
            
            # Seleciona o melhor
            winner_indice = participants_indices[np.argmax(participants_fitness)]
            selected.append(self.current_population[winner_indice])

        return np.array(selected)

    def crossover(self):
        """
        Realiza o cruzamento entre dois pais (one-point ou two-point).
        """
        np.random.shuffle(self.current_population)
        children = []
        n = len(self.current_population)
        i = 0
        while i < n - 1: # Parar antes do último se for ímpar
            parent1 = self.current_population[i]
            parent2 = self.current_population[i+1]

            if random.random() < self.crossover_rate:
    
                child1 = parent1.copy()
                child2 = parent2.copy()
                
                periods = np.shape(parent1)[0]

                rows_to_swap = random.sample(range(periods), periods//2)

                for row in rows_to_swap:
                    child1[row] = parent2[row].copy()
                    child2[row] = parent1[row].copy()

                children.extend([child1, child2])
            else:
                children.extend([parent1, parent2])
            i += 2
        self.current_population = np.array(children)

        if n % 2 == 1:
            children.append(self.current_population[-1])
        self.current_population = np.array(children)

    def mutation(self):
        """
        Aplica a mutação no indivíduo.
        """

        for idx, individual in enumerate(self.current_population):
                for i in range(np.shape(individual)[0]):
                    if random.random() < self.mutation_rate:

                        # Seleciona duas colunas aleatórias
                        columns_to_swap = random.sample(range(np.shape(individual)[1]), 2)
                        
                        # Troca as colunas
                        individual_copy =  individual[i, columns_to_swap[0]].copy()
                        individual[i, columns_to_swap[0]] = individual[i, columns_to_swap[1]]
                        individual[i, columns_to_swap[1]] = individual_copy

                        self.current_population[idx] = individual
                        
                        break

    def run(self, generations, update_callback=None):
        """
        Executa o algoritmo genético por um número definido de gerações.
        
        :param generations: Número de gerações a serem executadas.
        :return: O melhor indivíduo encontrado.
        """
        elite_individuals = None
        self.current_population = self.initialize_population()
        print(f"População inicial: {self.current_population}")
        print(f"Aptidão da população inicial: {self.fitness()}")
        for _ in range(generations):

            if self.stop and self.stop():
                break

            print(f"Geração {_ + 1}")
            
            # Calcula a aptidão de cada indivíduo, 
            fitness_values = self.fitness()
            print(f"Aptidão da população: {fitness_values}")

            # Elitismo: mantém os melhores indivíduos da geração anterior
            if self.elitism_count and self.elitism_count > 0:
                elite_indices = np.argsort(fitness_values)[-self.elitism_count:]
                elite_individuals = self.current_population[elite_indices]

            # Faz a seleção, crossover e mutação
            self.selection(fitness_values)
            self.crossover() 
            self.mutation()

            if elite_individuals is not None:
                new_fitness_values = self.real_function()
                worst_indices = np.argsort(new_fitness_values)[:self.elitism_count]
                for i, idx in enumerate(worst_indices):
                    self.current_population[idx] = elite_individuals[i]

            # Atualiza a população com os melhores indivíduos

            print(f"População após a mutação e elitismo: {self.current_population}")

            self.fitness()

            if update_callback:
                update_callback(
                    generation=_ + 1,
                    best_individual=self.best_individual,
                    best_fitness=self.best_fitness,
                    error=self.current_error if self.current_error is not None else 0
                )


            if self.max_known_value is not None and self.current_error < 1e-6:
                print(f"Encerrando o algoritmo, pois o erro é menor que 1e-6")
                break     

        return self.best_individual, self.best_fitness