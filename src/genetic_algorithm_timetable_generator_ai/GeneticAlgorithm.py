import numpy as np
import math
import random

class GeneticAlgorithm:
    def __init__(self, population_size, mutation_rate, crossover_rate, elitism_count = None, max_known_value = None,
                 selection_method='roulette', tournament_size=None, crossover_type='single_point', decimal_precision=1):
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
        self.bounds = [(-3.1, 12.1), (4.1, 5.8)]
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism_count = elitism_count
        self.selection_method = selection_method
        self.tournament_size = tournament_size
        self.crossover_type = crossover_type
        self.max_known_value = max_known_value
        self.best_individual = None
        self.best_fitness = None
        self.current_error = np.inf if max_known_value is not None else None
        self.mean_error = np.inf if max_known_value is not None else None
        self.decimal_precision = decimal_precision
        self.current_population = None
        self.stop = None # Callback para parar o algoritmo

    def real_function(self):
        """
        Função real a ser maximizada.
        """
        return 21.5 + self.current_population[:, 0] * np.sin(4 * np.pi * self.current_population[:, 0]) + self.current_population[:, 1] * np.sin(20 * np.pi * self.current_population[:, 1])

    def initialize_population(self):
        """
        Cria a população inicial de indivíduos.
        """

        # Inicialização
        return np.array([
            [np.round(np.random.uniform(low, high), self.decimal_precision) for (low, high) in self.bounds]
            for _ in range(self.population_size)
        ])
    
    def fitness(self):
        """
        Calcula a aptidão (fitness) da população.
        Atualiza o melhor indivíduo, o erro do melhor e o erro médio da população.
        """
        fitness_values = self.real_function()
        # Índice do melhor indivíduo
        best_idx = np.argmax(fitness_values)
        self.best_individual = self.current_population[best_idx]
        self.best_fitness = fitness_values[best_idx]

        if self.max_known_value is not None:
            # Erro do melhor indivíduo
            self.current_error = self.max_known_value - self.best_fitness
            # print(f"Erro do melhor indivíduo: {self.current_error}")
            # Erro médio da população
            self.mean_error = np.mean(self.max_known_value - fitness_values)
            # print(f"Erro médio da população: {self.mean_error}")
        else:
            self.current_error = None
            self.mean_error = None

        return fitness_values

    def get_n_bits(self, precision):
        """Calcula quantos bits são necessários para cada variável.

        :param precision: Precisão desejada para a conversão.

        :return: Lista com o número de bits necessários para cada variável.
        """
        bits = []
        for low, high in self.bounds:
            span = int((high - low) * (10**precision))
            bits.append(math.ceil(math.log2(span + 1)))
        return bits

    def real_to_bin(self, x, low, n_bits):
        """Converte valor real x para inteiro com precisão e depois para string binária.

        :param x: Valor real a ser convertido.
        :param low: Limite inferior da variável.
        :param n_bits: Número de bits disponíveis para a representação.

        :return: String binária representando o valor real.
        """
        factor = 10**self.decimal_precision
        x_int = int(round((x - low) * factor))
        return format(x_int, f'0{n_bits}b')

    def bin_to_real(self, bstr, low):
        """Converte string binária de volta para real, aplicando offset e precisão.

        :param bstr: String binária a ser convertida.
        :param low: Limite inferior da variável.
        :param n_bits: Número de bits disponíveis para a representação.

        :return: Valor real convertido.
        """
        factor = 10**self.decimal_precision
        return int(bstr, 2) / factor + low
    
    def clip_individual(self, individual):
        """
        Clipping do indivíduo para que ele não saia dos limites do problema.
        """

        # Fazer dessa forma habilita que o crossover ajuste o domínio para o problema independentemente da quantidade de variáveis
        lower_bounds = np.array([low for low, _ in self.bounds]) 
        upper_bounds = np.array([high for _, high in self.bounds])

        return np.clip(individual, lower_bounds, upper_bounds)
    
    def single_point_binary_crossover(self, parent1, parent2):
        """
        Realiza o cruzamento de ponto único entre dois indivíduos na representação binária.
        """
        precision = self.decimal_precision

        bits_list = self.get_n_bits(precision)
        
        # 1) Codifica cada indivíduo para representação binária
        b1 = ''
        b2 = ''
        for i in range(parent1.shape[0]):
            xp1, xp2 = parent1[i], parent2[i]
            low, _ = self.bounds[i]
            n_bits = bits_list[i]
            b1 += self.real_to_bin(xp1, low, n_bits)
            b2 += self.real_to_bin(xp2, low, n_bits)

        # 2) Escolhe um ponto de corte aleatório
        point = random.randint(1, len(b1) - 1)
        
        # 3) Realiza o cruzamento
        child_bin = b1[:point] + b2[point:]
        
        # 4) Decodifica o filho de volta para valores reais
        child = []
        idx = 0 # Começa na posição 0
        for i, (low, _) in enumerate(self.bounds):
            n_bits = bits_list[i]
            snippet = child_bin[idx:idx+n_bits]
            child.append(self.bin_to_real(snippet, low))
            idx += n_bits

        return self.clip_individual(np.array(child))

    def double_point_binary_crossover(self, parent1, parent2):

        """
        Realiza o cruzamento de dois pontos entre dois indivíduos na representação binária.
        
        :param p1: Primeiro pai (array de valores reais)
        :param p2: Segundo pai (array de valores reais)
        :param bounds: Lista de tuplas com os limites (min, max) de cada variável
        :param precision: Precisão decimal para a codificação binária
        :return: Filho resultante do cruzamento (array de valores reais)
        """
        # Determina o número de bits necessários para cada variável
        bits_list = self.get_n_bits(self.decimal_precision)
        
        # 1) Codifica cada indivíduo para representação binária
        b1 = ''
        b2 = ''
        for i in range(parent1.shape[0]):
            xp1, xp2 = parent1[i], parent2[i]
            low, _ = self.bounds[i]
            n_bits = bits_list[i]
            b1 += self.real_to_bin(xp1, low, n_bits)
            b2 += self.real_to_bin(xp2, low, n_bits)
    
        # 2) Escolhe dois pontos de corte aleatórios
        a, b = sorted(random.sample(range(1, len(b1)), 2)) # Ordena os pontos para que a seja o menor
        
        # 3) Realiza o cruzamento
        child_bin = b1[:a] + b2[a:b] + b1[b:]

        # Exemplo caso a = 2 e b = 5 e len(b1) = 8
        # b1 = 11100011
        # b2 = 00111100
        # child_bin = 11|111|011
        #             ^^|^^^|^^^
        #             b1|b2 |b1

        # 4) Decodifica o filho de volta para valores reais
        child = []
        idx = 0
        for i, (low, _) in enumerate(self.bounds):
            n_bits = bits_list[i]
            snippet = child_bin[idx:idx+n_bits]
            child.append(self.bin_to_real(snippet, low))
            idx += n_bits

        return self.clip_individual(np.array(child))

    def selection(self, fitness_values):
        """
        Seleciona os indivíduos para reprodução, com base no método definido.
        """
        # TODO implementar o elitismo

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
                if self.crossover_type == 'single_point':
                    child1 = self.single_point_binary_crossover(parent1, parent2)
                    child2 = self.single_point_binary_crossover(parent2, parent1)       
                elif self.crossover_type == 'double_point':
                    child1 = self.double_point_binary_crossover(parent1, parent2)
                    child2 = self.double_point_binary_crossover(parent2, parent1)
                else:
                    raise ValueError("Invalid crossover type")
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
            for i in range(len(individual)):
                if random.random() < self.mutation_rate:
                    binary_individual = list(self.real_to_bin(
                        individual[i], 
                        self.bounds[i][0], 
                        self.get_n_bits(self.decimal_precision)[i]
                    ))
                    point = random.randint(0, len(binary_individual) - 1)
                    binary_individual[point] = '1' if binary_individual[point] == '0' else '0'
                    binary_individual = ''.join(binary_individual)
                    individual[i] = self.bin_to_real(binary_individual, self.bounds[i][0])
                    individual = self.clip_individual(individual)
                    self.current_population[idx] = individual
        

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