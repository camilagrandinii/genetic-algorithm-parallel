import os
import time
import numpy as np
from mpi4py import MPI
from Arquivo import Arquivo
from diretorio import Diretorio
from MOGAToolbox import MOGAToolbox as mt
from ExperimentsGen import ExperimentsGen
from ParallelManager import ParallelManager
from utils.ParamsExtracter import ParamsExtracter

# ====== MARK: Defining paths and file names ======
DIRETORIO_PATH = os.path.abspath(".outputs")
EXPERIMENTO_PATH = os.path.abspath("./Experimentos")

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    processor_name = MPI.Get_processor_name()  # Obtains processor name
    
    if size < 3:
        print("Erro: Este script requer pelo menos 3 processos MPI (1 mestre, 2+ escravos).")
        comm.Abort(1)
        
    print(f"Hello from process {rank} out of {size} on {processor_name}")

    start_time = time.time()
    diretorio = Diretorio(DIRETORIO_PATH)
    diretorio.create_folder(EXPERIMENTO_PATH)
    params_extracter = ParamsExtracter()

    # Leitura dos arquivos
    arquivo = Arquivo()

    # Leitura e parsing da primeira linha
    linhas_arquivo = arquivo.le_arquivo_teste()
    name_test_file, class_name_test_file = linhas_arquivo[0].strip().split()

    # Configura o arquivo e nome da classe
    arquivo.le_arquivo(name_test_file)
    arquivo.set_nome_classe_arquivo_teste(class_name_test_file)

    # Define constantes relacionadas ao conjunto de dados
    SAMPLE_COUNT = arquivo.quantidade_linhas_colunas(0)
    INDIVIDUAL_SIZE = arquivo.quantidade_linhas_colunas(1) - 1

    # Setup do ambiente de GA
    mt.setup_creator()

    # Preparando os parâmetros do GA
    backup = params_extracter.parse_line(linhas_arquivo[1])
    seed = params_extracter.parse_line(linhas_arquivo[2], skip_first=True)
    Population = params_extracter.parse_line(linhas_arquivo[3])
    Generations = params_extracter.parse_line(linhas_arquivo[4])
    CrossOverFactor = params_extracter.parse_line(linhas_arquivo[5])
    TournamentSize = params_extracter.parse_line(linhas_arquivo[6], skip_first=True)
    MutationRate = params_extracter.parse_line(linhas_arquivo[7])
    ElitismFactor = params_extracter.parse_line(linhas_arquivo[8], skip_first=True)
    ml_model_params = params_extracter.parse_line(linhas_arquivo[9])

    population_min, population_max, population_ite = (
        params_extracter.extract_param_values(Population)
    )
    generations_min, generation_max, generation_ite = (
        params_extracter.extract_param_values(Generations)
    )
    crossover_min, crossover_max, crossover_ite = params_extracter.extract_param_values(
        CrossOverFactor
    )
    mutation_min, mutation_max, mutation_ite = params_extracter.extract_param_values(
        MutationRate
    )

    classifier_name = ml_model_params[0]
    population_values = np.arange(
        int(population_min), int(population_max), int(population_ite)
    )
    generations_num = np.arange(
        int(generations_min), int(generation_max), int(generation_ite)
    )
    cross_rates = np.arange(
        float(crossover_min), float(crossover_max), float(crossover_ite)
    )
    mut_rates = np.arange(
        float(mutation_min), float(mutation_max), float(mutation_ite)
    )

    experiment_generator = ExperimentsGen(
        INDIVIDUAL_SIZE, SAMPLE_COUNT,
        seed, population_values, generations_num, 
        cross_rates, mut_rates, 
        backup, TournamentSize, 
        classifier_name, ml_model_params,
        name_test_file, class_name_test_file
    )

    experiments = experiment_generator.generate_all_experiments(backup)
    
    parallel_manager = ParallelManager(
        comm_parallel=comm,
        size_parallel=size,
        rank_parallel=rank,
        experiments=experiments,
        name_test_file=name_test_file,
        class_name_test_file=class_name_test_file,
        individual_size=INDIVIDUAL_SIZE,
        start_time=start_time
    )
    
    parallel_manager.run()

if __name__ == "__main__":
    main()
