# Standard Library Imports
import array
import csv
import os
import random
import numpy as np
import time
import sys

# Third-party Library Imports
from deap import base, creator, tools

# Local Imports
from MultiObjectiveGeneticAlgorithm import MultiObjectiveGeneticAlgorithm
from MOGAToolbox import MOGAToolbox as mt
from Arquivo import Arquivo
from algoritmo_Genetico import Algoritmo_Genetico
from algoritmos_ML import AlgoritmosML
from diretorio import Diretorio
from rankeamento import Rankeamento
from valida import valida_experimento
from encontra_melhor import Encontra_melhor

# ====== MARK: Defining paths and file names ======
CLASSIFIER_PATH = os.path.abspath("Individuos")
DIRETORIO_PATH = os.path.abspath(".outputs")
EXPERIMENTO_PATH = os.path.abspath("./Experimentos")
EXPERIMENTO_PATH_ = os.path.abspath("./Experimentos")
RESULTADOS_PATH = os.path.abspath("./Resultados_teste")

HALL_OF_FAME_SIZE = 10

def main():
    start_time = time.time()
    diretorio = Diretorio(DIRETORIO_PATH)
    diretorio.create_folder(EXPERIMENTO_PATH)

    # Leitura dos arquivos
    arquivo = Arquivo()
    linhas_arquivo = arquivo.le_arquivo_teste()
    arquivo_csv = linhas_arquivo[0].strip("\n").split(' ')
    nome_arquivo_teste = arquivo_csv[0]
    nome_classe_arquivo_teste = arquivo_csv[1]
    arquivo.le_arquivo(nome_arquivo_teste)    
    arquivo.set_nome_classe_arquivo_teste(nome_classe_arquivo_teste)
    SAMPLE_COUNT = arquivo.quantidade_linhas_colunas(0)
    INDIVIDUAL_SIZE = arquivo.quantidade_linhas_colunas(1) - 1
    mt.setup_creator()

    # Preparando os elementos para entrar no teste
    backup = linhas_arquivo[1].strip("\n").split(" ")
    seed = linhas_arquivo[2].strip("\n").split(" ")
    seed.pop(0)
    Population = linhas_arquivo[3].strip("\n").split(" ")
    Generations = linhas_arquivo[4].strip("\n").split(" ")
    CrossOverFactor = linhas_arquivo[5].strip("\n").split(" ")
    TournamentSize = linhas_arquivo[6].strip("\n").split(" ")
    TournamentSize.pop(0)
    MutationRate = linhas_arquivo[7].strip("\n").split(" ")
    ElitismFactor = linhas_arquivo[8].strip("\n").split(" ")
    ElitismFactor.pop(0)
    algoritmo_Ml = linhas_arquivo[9].strip("\n").split(" ")

    population_min = Population[1].strip()
    population_max = Population[2].strip()
    population_ite = Population[3].strip()
    generations_min = Generations[1].strip()
    generation_max = Generations[2].strip()
    generation_ite = Generations[3].strip()
    crossover_min = CrossOverFactor[1].strip()
    crossover_max = CrossOverFactor[2].strip()
    crossover_ite = CrossOverFactor[3].strip()
    mutation_min = MutationRate[1].strip()
    mutation_max = MutationRate[2].strip()
    mutation_ite = MutationRate[3].strip()

    nome_classificador = algoritmo_Ml[0]
    algoritmo_ml = AlgoritmosML(nome_classificador, algoritmo_Ml)
    modelo_ml = algoritmo_ml.get_model()
    hall_of_fame = tools.HallOfFame(HALL_OF_FAME_SIZE)

    todos_fitness = []
    contador = 0

    # Lógica de backup
    retomar = int(backup[0]) == 0
    skip = retomar
    if retomar:
        conteudo = Arquivo.le_arquivo_txt(backup[1]).split("\n")
        seed_resume = conteudo[0].split(":")[1]
        pop_resume = int(conteudo[1].split(":")[1])
        gen_resume = int(conteudo[2].split(":")[1])
        cross_resume = float(conteudo[3].split(":")[1])
        mut_resume = float(conteudo[4].split(":")[1])
        contador = int(conteudo[5].split(":")[1])

    for seed_val in seed:
        CLASSIFIER_FILE_NAME = seed_val + ".csv"
        for pop_size in np.arange(int(population_min), int(population_max), int(population_ite)):
            if pop_size % 4 != 0:
                continue
            for num_gen in np.arange(int(generations_min), int(generation_max), int(generation_ite)):
                for cross_rate in np.arange(float(crossover_min), float(crossover_max), float(crossover_ite)):
                    for mut_rate in np.arange(float(mutation_min), float(mutation_max), float(mutation_ite)):

                        if skip:
                            if seed_val != seed_resume: continue
                            if pop_size != pop_resume: continue
                            if num_gen != gen_resume: continue
                            if round(cross_rate, 3) != round(cross_resume, 3): continue
                            if round(mut_rate, 3) != round(mut_resume, 3): continue
                            skip = False

                        parametros = f"i:{seed_val}\nj:{pop_size}\nk:{num_gen}\nl:{cross_rate}\nm:{mut_rate}\ncontador:{contador}"
                        Arquivo.escreve_arquivo_backup(backup[1], parametros)

                        cross_rate = round(cross_rate, 3)
                        mut_rate = round(mut_rate, 3)
                        random.seed(seed_val)

                        path = f"Experimento_{contador}"
                        diretorio.create_folder_in_folder(path)
                        FILE_NAME = f"seed_{seed_val}_pop_{pop_size}_gen_{num_gen}_cross_{cross_rate}_muta_{mut_rate}"

                        evolution_toolbox = mt(
                            INDIVIDUAL_SIZE,
                            mut_rate,
                            CLASSIFIER_FILE_NAME,
                            CLASSIFIER_PATH,
                            SAMPLE_COUNT,
                            TournamentSize[0],
                            arquivo,
                            modelo_ml,
                            FILE_NAME,
                            diretorio,
                            todos_fitness,
                            num_gen
                        ).toolbox

                        population = evolution_toolbox.population(n=pop_size)
                        for individual in population:
                            individual.pais = []

                        stats1 = tools.Statistics(lambda ind: ind.fitness.values)
                        stats1.register("1) Media   ", np.mean, axis=0)
                        stats1.register("2) Desvio Padrao   ", np.std, axis=0)
                        stats1.register("3) Minimo  ", np.min, axis=0)
                        stats1.register("4) Maximo  ", np.max, axis=0)

                        stats2 = tools.Statistics(lambda ind: ind)
                        stats2.register("Piores / Melhores  ", Algoritmo_Genetico.count_individuals_relative_to_parent_average)
                        stats2.register("Ind. Repetidos\t ", Algoritmo_Genetico.get_duplicate_individuals_count)

                        stats = tools.MultiStatistics(Fitness=stats1, Filhos=stats2)

                        print("Starting algorithm...")
                        multi_objective_genetic_algorithm = MultiObjectiveGeneticAlgorithm(
                            seed_val,
                            population,
                            evolution_toolbox,
                            cross_rate,
                            mut_rate,
                            num_gen,
                            pop_size,
                            diretorio,
                            stats=stats,
                            hall_of_fame=hall_of_fame,
                            FILE_NAME=FILE_NAME
                        )

                        multi_objective_genetic_algorithm.execute()

                        melhores_path = "Melhores_" + FILE_NAME + ".txt"
                        diretorio_melhores = diretorio.constroi_caminho(diretorio.get_path(), melhores_path)
                        with open(diretorio_melhores, "w") as best_individuals:
                            for top_individual in hall_of_fame[1:]:
                                best_individuals.write(
                                    str(top_individual) + str(top_individual.fitness.values) + "\n"
                                )

                        print("\nDone!")

                        duration = time.time() - start_time
                        hours, remainder = divmod(duration, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        print(f"Total execution time: {int(hours)}h {int(minutes)}m {int(seconds)}s")

                        contador += 1

    # Rankeamento final
    rank = Rankeamento()
    diretorio.remove_arquivos(RESULTADOS_PATH)
    rank.junta_arquivos(EXPERIMENTO_PATH_, RESULTADOS_PATH)
    colunas = rank.processa_arquivos_teste(EXPERIMENTO_PATH_, RESULTADOS_PATH, INDIVIDUAL_SIZE)
    colunas_para_filtrar = [item[0] for item in colunas]  
    colunas_tratadas = [int(coluna.split(" ")[-1].strip()) for coluna in colunas_para_filtrar]
    validacao = valida_experimento()
    dataset = arquivo.retorna_dataset()
    validacao.valida_sem_salvar_modelo(dataset, nome_classe_arquivo_teste, colunas_tratadas)
    melhor_individuo = Encontra_melhor()
    lista_individuos = melhor_individuo.encontra_melhores_individuos(RESULTADOS_PATH)
    resultados = melhor_individuo.avalia_individuos(arquivo, lista_individuos, nome_classe_arquivo_teste)
    resultados.sort(key=lambda x: x['f1_score'], reverse=True)
    print("\nMelhor indivíduo encontrado:")
    print(f"F1-score: {resultados[0]['f1_score']:.4f}")
    print(f"Qtd atributos: {resultados[0]['qtd_atributos']}")
    print(f"Atributos selecionados: {resultados[0]['nomes_colunas']}")
    print(f"Arquivo de origem: {resultados[0]['arquivo_origem']}")


if __name__ == "__main__":
    main()