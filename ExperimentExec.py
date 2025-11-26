import os
import time
import random
import numpy as np
from deap import tools
from Arquivo import Arquivo
from diretorio import Diretorio
from algoritmos_ML import AlgoritmosML
from MOGAToolbox import MOGAToolbox as mt
from algoritmo_Genetico import Algoritmo_Genetico
from MultiObjectiveGeneticAlgorithm import MultiObjectiveGeneticAlgorithm

HALL_OF_FAME_SIZE = 10
EXPERIMENTO_PATH = os.path.abspath("./Experimentos")
    
class ExperimentExec:
    def __init__(
        self,
        experiment_configuration,
        start_time
    ):
        """
        Inicializa com os parâmetros necessários para executar o experimento
        """
        self.experiment_configuration = experiment_configuration
        self.start_time = start_time
    
    def _prepare_experiment_components(self):
        # Setup diretório
        diretorio = Diretorio(self.experiment_configuration.output_base_dir)
        path = f"Experimento_{self.experiment_configuration.experiment_count}"
        diretorio.create_folder(EXPERIMENTO_PATH)
        diretorio.create_folder_in_folder(path)
        output_path = diretorio.constroi_caminho(diretorio.get_path(), path)

        arquivo = Arquivo()
        arquivo.le_arquivo(self.experiment_configuration.name_test_file)
        arquivo.set_nome_classe_arquivo_teste(self.experiment_configuration.class_name_test_file)

        # Setup ML
        mt.setup_creator()
        algoritmo_ml = AlgoritmosML(self.experiment_configuration.classifier_name, self.experiment_configuration.ml_model_params)
        modelo_ml = algoritmo_ml.get_model()

        # FILE_NAME base
        file_name = f"seed_{self.experiment_configuration.seed}_pop_{self.experiment_configuration.pop_size}_gen_{self.experiment_configuration.num_gen}_cross_{self.experiment_configuration.cross_rate}_muta_{self.experiment_configuration.mut_rate}"
        classifier_file_name = f"{self.experiment_configuration.seed}.csv"

        # Toolbox e população
        toolbox = mt(
            self.experiment_configuration.individual_size,
            self.experiment_configuration.mut_rate,
            classifier_file_name,
            self.experiment_configuration.classifier_path,
            self.experiment_configuration.sample_count,
            self.experiment_configuration.tournament_size,
            arquivo,
            modelo_ml,
            file_name,
            diretorio,
            [],
            self.experiment_configuration.num_gen,
        ).toolbox

        population = toolbox.population(n=self.experiment_configuration.pop_size)
        for individual in population:
            individual.pais = []

        # Estatísticas
        stats1 = tools.Statistics(lambda ind: ind.fitness.values)
        stats1.register("1) Media   ", np.mean, axis=0)
        stats1.register("2) Desvio Padrao   ", np.std, axis=0)
        stats1.register("3) Minimo  ", np.min, axis=0)
        stats1.register("4) Maximo  ", np.max, axis=0)

        stats2 = tools.Statistics(lambda ind: ind)
        stats2.register("Piores / Melhores  ", Algoritmo_Genetico.count_individuals_relative_to_parent_average)
        stats2.register("Ind. Repetidos\t ", Algoritmo_Genetico.get_duplicate_individuals_count)

        stats = tools.MultiStatistics(Fitness=stats1, Filhos=stats2)

        hall_of_fame = tools.HallOfFame(HALL_OF_FAME_SIZE)

        return {
            "diretorio": diretorio,
            "arquivo": arquivo,
            "modelo_ml": modelo_ml,
            "toolbox": toolbox,
            "population": population,
            "stats": stats,
            "hall_of_fame": hall_of_fame,
            "file_name": file_name,
            "output_path": output_path
        }
    
    def execute_experiment(self):
        random.seed(self.experiment_configuration.seed)
        
        components = self._prepare_experiment_components()
        
        print("Starting algorithm...")
        print(f"[DEBUG][ExperimentExec] output_base_dir = {self.experiment_configuration.output_base_dir}")
        print(f"[DEBUG] cwd={os.getcwd()}")

        ga = MultiObjectiveGeneticAlgorithm(
            seed=self.experiment_configuration.seed,
            population=components["population"],
            evolution_toolbox=components["toolbox"],
            crossover_probability=self.experiment_configuration.cross_rate,
            mutation_probability=self.experiment_configuration.mut_rate,
            generation_count=self.experiment_configuration.num_gen,
            population_size=self.experiment_configuration.pop_size,
            diretorio=components["diretorio"],
            stats=components["stats"],
            hall_of_fame=components["hall_of_fame"],
            FILE_NAME=components["file_name"],
        )

        ga.execute()

        # Salvar melhores
        melhores_path = f"Melhores_{components['file_name']}.txt"
        out_path = components["diretorio"].constroi_caminho(
            components["diretorio"].get_path(), melhores_path
        )
        print("returned hall of fame: ", components["hall_of_fame"])
        with open(out_path, "w") as best_individuals:
            for top_individual in components["hall_of_fame"][1:]:
                best_individuals.write(str(top_individual) + str(top_individual.fitness.values) + "\n")
        
        duration = time.time() - self.start_time
        hours, remainder = divmod(duration, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(f"Total execution time: {int(hours)}h {int(minutes)}m {int(seconds)}s")

        print("Experimento finalizado.")
