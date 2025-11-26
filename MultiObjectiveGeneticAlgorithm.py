import random
import datetime
import numpy as np
from deap import tools
from scipy.spatial import distance
from classificadorT import ClassificadorT
from deap.tools.emo import sortNondominated
from MOGATerminalLogger import MOGATerminalLogger

class MultiObjectiveGeneticAlgorithm:

    def __init__(
        self,
        seed,
        population,
        evolution_toolbox,
        crossover_probability,
        mutation_probability,
        generation_count,
        population_size,
        diretorio,
        stats=None,
        hall_of_fame=None,
        verbose=__debug__,
        FILE_NAME="TESTE"
    ):
        self.population = population
        self.seed = seed
        self.evolution_toolbox = evolution_toolbox
        self.crossover_probability = crossover_probability
        self.mutation_probability = mutation_probability
        self.generation_count = generation_count
        self.population_size = population_size
        self.diretorio = diretorio
        self.stats = stats
        self.hall_of_fame = hall_of_fame
        self.verbose = verbose
        self.FILE_NAME = FILE_NAME

        # Inicialização para convergência dinâmica
        self.prev_pareto = []
        self.no_change_count = 0
        self.stop_threshold = 0.1  # Limiar para considerar a convergência
        self.patience = 10

    def remove_individuals_with_zero_fitness_and_adjust_population(self, population: list, original_population_size: int):
        """Remove indivíduos com fitness igual a zero e ajusta a população."""
        population = [ind for ind in population if ind.fitness.values[1] != 0]

        while len(population) < original_population_size:
            seed = random.randrange(0, len(population))
            copy_of_individual = population[seed]
            population.append(copy_of_individual)
        return population

    # def pareto_variation(self, prev_pareto, curr_pareto):
    #     """Calcula a variação entre a Fronteira de Pareto da geração atual e da anterior."""
    #     if not prev_pareto:
    #         return np.inf  # Primeira geração, não há referência anterior

    #     prev_points = np.array([ind.fitness.values for ind in prev_pareto])
    #     curr_points = np.array([ind.fitness.values for ind in curr_pareto])

    #     return np.linalg.norm(prev_points - curr_points, axis=1).mean()

    def pareto_variation(self, prev_pareto, curr_pareto):
        if not prev_pareto:
            return np.inf  # Primeira geração, não há referência anterior

        prev_points = np.array([ind.fitness.values for ind in prev_pareto])
        curr_points = np.array([ind.fitness.values for ind in curr_pareto])

        # Calcula a menor distância entre cada ponto da nova fronteira e a fronteira anterior
        distancias = [min(distance.cdist([p], prev_points, metric='euclidean')[0]) for p in curr_points]

        return np.mean(distancias)  # Retorna a média das distâncias

    def apply_variation_crossover_mutation(self, population):
        """Aplica operadores de crossover e mutação na população."""
        offspring = [self.evolution_toolbox.clone(individual) for individual in population]

        # Aplica crossover
        for i in range(1, len(offspring), 2):
            if random.random() < self.crossover_probability:
                offspring[i - 1], offspring[i] = self.evolution_toolbox.mate(offspring[i - 1], offspring[i])
                del offspring[i - 1].fitness.values, offspring[i].fitness.values

        # Aplica mutação
        for i in range(len(offspring)):
            if random.random() < self.mutation_probability:
                (offspring[i],) = self.evolution_toolbox.mutate(offspring[i])
                del offspring[i].fitness.values

        return offspring

    def execute(self):
        """Executa o Algoritmo Genético Multiobjetivo."""
        clt = ClassificadorT()
        logbook = tools.Logbook()
        num_generation_atual = 0
        clt.set_num_geracao(num_generation_atual)

        logbook.header = ["gen", "nevals"] + (self.stats.fields if self.stats else [])

        # Avaliação inicial dos indivíduos
        invalid_individuals = [ind for ind in self.population if not ind.fitness.valid]
        fitnesses = self.evolution_toolbox.map(self.evolution_toolbox.evaluate, invalid_individuals)

        for individual, fitness in zip(invalid_individuals, fitnesses):
            individual.fitness.values = fitness

        self.population = self.remove_individuals_with_zero_fitness_and_adjust_population(self.population, self.population_size)

        if self.hall_of_fame is not None:
            self.hall_of_fame.update(self.population)

        record = self.stats.compile(self.population) if self.stats else {}
        logbook.record(gen=0, nevals=len(invalid_individuals), **record)
        MOGATerminalLogger.print_generation_results(0, len(self.population), record, self.diretorio, self.FILE_NAME)

        self.population = self.evolution_toolbox.select(self.population, self.population_size)

        # Início do loop de gerações
        for generation_number in range(1, self.generation_count + 1):
            num_generation_atual = generation_number
            clt.set_num_geracao(num_generation_atual)

            offspring = tools.selTournamentDCD(self.population, len(self.population))

            # Aplica crossover e mutação
            offspring = self.apply_variation_crossover_mutation(offspring)

            self.log_generation(generation_number)

            # Avaliação dos indivíduos inválidos
            invalid_individuals = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = self.evolution_toolbox.map(self.evolution_toolbox.evaluate, invalid_individuals)

            for individual, fitness in zip(invalid_individuals, fitnesses):
                individual.fitness.values = fitness

            offspring = self.remove_individuals_with_zero_fitness_and_adjust_population(offspring, self.population_size)

            if self.hall_of_fame is not None:
                self.hall_of_fame.update(offspring)

            self.population = self.evolution_toolbox.select(self.population + offspring, self.population_size)

            record = self.stats.compile(self.population) if self.stats else {}
            logbook.record(gen=generation_number, nevals=len(invalid_individuals), **record)
            MOGATerminalLogger.print_generation_results(generation_number, len(self.population), record, self.diretorio, self.FILE_NAME)

            # Cálculo da variação da Fronteira de Pareto
            curr_pareto = sortNondominated(self.population, len(self.population), first_front_only=True)[0]
            variation = self.pareto_variation(self.prev_pareto, curr_pareto)
            print(f"Geração {generation_number}: Variação da Fronteira de Pareto = {variation}")

            # Critério de parada baseado na convergência
            if variation < self.stop_threshold:
                self.no_change_count += 1
            else:
                self.no_change_count = 0  # Reset se houver mudança significativa

            if self.no_change_count >= self.patience:
                print(f"Convergência detectada na geração {generation_number}!")
                break

            self.prev_pareto = curr_pareto.copy()

        return self.population, logbook

    def log_generation(self, generation_number):
        """Registra a geração atual em um arquivo de log."""
        with open("log/Geracao_" + self.FILE_NAME + ".txt", "a+") as GENERATION_LOG:
            GENERATION_LOG.write(
                f"Classificando geração: {generation_number} Hora: {datetime.datetime.now()}\n"
            )
