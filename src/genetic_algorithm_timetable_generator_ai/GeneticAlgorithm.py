import numpy as np
import math
import random
from subject import Subject
from timetable import Timetable
from mock_data import subjects, period_subjects

class GeneticAlgorithm:
    def __init__(self, population_size, mutation_rate, crossover_rate, elitism_count = None,
                 selection_method='roulette', tournament_size=None):
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
        self.total_slots = self.num_days * self.num_slots
        
        # Informações sobre as disciplinas
        self.subjects = subjects
        self.period_subjects = period_subjects
        
        # Criar disciplinas vazias para cada período
        self.empty_slots = {
            period: Subject.create_empty_slot(period)
            for period in range(1, self.num_periods + 1)
        }

    def initialize_population(self):
        """
        Cria a população inicial de indivíduos.
        """
        if not all([self.subjects, self.period_subjects]):
            raise ValueError("As informações de disciplinas devem ser definidas antes de inicializar a população")

        population = np.array([])
        
        for _ in range(self.population_size):
            timetable = Timetable(self.num_periods, self.num_days, self.num_slots)
            
            # Para cada período
            for period in range(self.num_periods):
                # Obtém as disciplinas deste período
                period_subjects = self.period_subjects[period + 1]  # +1 porque os períodos começam em 1
                
                # Para cada disciplina do período
                for subject_id in period_subjects:
                    subject = next(s for s in self.subjects if s.id == subject_id) # Next é usado para pegar o primeiro elemento da lista que corresponde ao id da disciplina
                    
                    # Distribui as aulas da disciplina ao longo da semana
                    remaining_classes = subject.workload
                    
                    while remaining_classes > 0:
                        # Escolhe aleatoriamente um dia e horário
                        day = random.randint(0, self.num_days - 1)
                        slot = random.randint(0, self.num_slots - 1)
                        
                        # Se o horário estiver vazio
                        if timetable.is_slot_empty(period, day, slot):
                            timetable.set_subject_at(period, day, slot, subject.id)
                            remaining_classes -= 1
                
                # Preenche os horários restantes com disciplinas vazias
                empty_slots = timetable.count_empty_slots(period)
                for _ in range(empty_slots):
                    day = random.randint(0, self.num_days - 1)
                    slot = random.randint(0, self.num_slots - 1)
                    if timetable.is_slot_empty(period, day, slot):
                        timetable.set_subject_at(period, day, slot, self.empty_slots[period + 1].id)
            
            population = np.append(population, timetable)
        
        return population

    def fitness_function(self):
        """
        Função real a ser maximizada.
        """
        fitness_values = []
        
        for timetable in self.current_population:
            conflicts = self.count_conflicts(timetable)
            gaps = self.count_gaps(timetable)
            consecutive = self.count_consecutive_classes(timetable)
            
            fitness = 500 - 20 * conflicts - 5 * gaps + 10 * consecutive
            fitness_values.append(fitness)
        
        return np.array(fitness_values)

    def count_conflicts(self, timetable):
        """
        Conta o número de conflitos entre os horários dos professores.
        """
        conflicts = 0
        
        for period in range(self.num_periods):
            for day in range(self.num_days):
                for slot in range(self.num_slots):
                    subject_id = timetable.get_subject_at(period, day, slot)
                    if subject_id == 0:  # Ignora slots vazios
                        continue
                        
                    subject = next(s for s in self.subjects if s.id == subject_id)
                    if subject.is_empty_slot:
                        continue
                    
                    # Verifica se o mesmo professor está dando aula em outro período no mesmo horário
                    for other_period in range(self.num_periods):
                        if other_period == period:
                            continue
                            
                        other_subject_id = timetable.get_subject_at(other_period, day, slot)
                        if other_subject_id == 0:
                            continue
                            
                        other_subject = next(s for s in self.subjects if s.id == other_subject_id)
                        if other_subject.is_empty_slot:
                            continue
                            
                        if subject.teacher == other_subject.teacher:
                            conflicts += 1
        
        return conflicts

    def count_gaps(self, timetable):
        """
        Conta o número de gaps entre as aulas com penalizações e bônus específicos.
        """
        score = 0
        
        for period in range(self.num_periods):
            for day in range(self.num_days):
                # Verifica slots 1-2 juntos
                if (timetable.is_slot_empty(period, day, 0) and 
                    timetable.is_slot_empty(period, day, 1)):
                    score += 15  # Bônus grande para vagos 1-2
                
                # Verifica slots 3-4 juntos
                if (timetable.is_slot_empty(period, day, 2) and 
                    timetable.is_slot_empty(period, day, 3)):
                    score += 15  # Bônus grande para vagos 3-4
                
                # Verifica slots 2-3 juntos
                if (timetable.is_slot_empty(period, day, 1) and 
                    timetable.is_slot_empty(period, day, 2)):
                    score -= 20  # Penalidade forte para vagos 2-3
                
                # Verifica slots individuais
                for slot in range(self.num_slots):
                    if timetable.is_slot_empty(period, day, slot):
                        if slot in [0, 3]:  # Slots 1 ou 4
                            score += 5  # Pequeno bônus
                        elif slot in [1, 2]:  # Slots 2 ou 3
                            score -= 10  # Penalidade
        
        return -score  # Retorna negativo porque queremos maximizar o fitness

    def count_consecutive_classes(self, timetable):
        """
        Conta o número de aulas consecutivas da mesma disciplina.
        """
        consecutive = 0
        
        for period in range(self.num_periods):
            for day in range(self.num_days):
                current_subject = None
                current_count = 0
                
                for slot in range(self.num_slots):
                    subject_id = timetable.get_subject_at(period, day, slot)
                    if subject_id == 0:
                        continue
                        
                    subject = next(s for s in self.subjects if s.id == subject_id)
                    if subject.is_empty_slot:
                        continue
                    
                    if subject.id == current_subject:
                        current_count += 1
                        if current_count > 1:
                            consecutive += 1
                    else:
                        current_subject = subject.id
                        current_count = 1
        
        return consecutive

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

        # TODO : Adaptar o crossover
        np.random.shuffle(self.current_population)
        children = []
        n = len(self.current_population)
        i = 0
        while i < n - 1: # Parar antes do último se for ímpar
            parent1 = self.current_population[i]
            parent2 = self.current_population[i+1]

            if random.random() < self.crossover_rate:
    
                child1 = parent1
                child2 = parent2
                
                print(f"Parent1: {parent1}")

                periods = parent1.num_periods

                rows_to_swap = random.sample(range(periods), periods//2)

                for row in rows_to_swap:
                    child1.schedule[row] = parent2.schedule[row]
                    child2.schedule[row] = parent1.schedule[row]

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

        # TODO : Adaptar a mutação

        for idx, individual in enumerate(self.current_population):
            for i in range(individual.num_periods):
                if random.random() < self.mutation_rate:

                    # Seleciona duas colunas aleatórias
                    columns_to_swap = random.sample(range(individual.total_slots), 2)
                        
                    # Troca as colunas
                    individual_copy =  individual.schedule[i, columns_to_swap[0]]
                    individual.schedule[i, columns_to_swap[0]] = individual.schedule[i, columns_to_swap[1]]
                    individual.schedule[i, columns_to_swap[1]] = individual_copy

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
                print(f"Elitismo: {self.elitism_count}")
                elite_indices = np.argsort(fitness_values)[-self.elitism_count:]
                print(f"Índices dos indivíduos elitistas: {elite_indices}")
                elite_individuals = self.current_population[elite_indices]

            # Faz a seleção, crossover e mutação
            self.selection(fitness_values)
            self.crossover() 
            self.mutation()

            if elite_individuals is not None:
                new_fitness_values = self.fitness_function()
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
                    best_fitness=self.best_fitness
                )

        return self.best_individual, self.best_fitness