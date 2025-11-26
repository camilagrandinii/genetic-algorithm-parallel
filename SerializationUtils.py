import os
import re
from deap import creator

class SerializationUtils:
    def read_best_individuals(parallel_rank, experiments_folder):
        """
        Lê os arquivos que contenham 'melhores' no nome dentro da pasta experiments_folder,
        reconstrói os indivíduos com genótipo e fitness.
        """
        print(f"[DEBUG][Rank {parallel_rank}] Pasta atual: {os.getcwd()}")
        padrao = r"Individual\('i',\s*\[(.*?)\]\)\(np\.float64\((.*?)\),\s*(.*?)\)"
        individuos = []

        for nome_arquivo in os.listdir(experiments_folder):
            if "melhores" in nome_arquivo.lower() and nome_arquivo.endswith(".txt"):
                caminho_arquivo = os.path.join(experiments_folder, nome_arquivo)

                with open(caminho_arquivo, 'r') as f:
                    for linha in f:
                        match = re.search(padrao, linha)
                        if match:
                            bits = list(map(int, match.group(1).split(',')))
                            fit1 = float(match.group(2))
                            fit2 = float(match.group(3))
                            fitness = (fit1, fit2)

                            ind = creator.Individual(bits)
                            ind.fitness.values = fitness
                            individuos.append(ind)

                print(f"[INFO] Leu {len(individuos)} indivíduos de '{nome_arquivo}'")
                return individuos  # Para o primeiro arquivo encontrado

        print("[WARN] Nenhum arquivo com 'melhores' encontrado em:", experiments_folder)
        return []
    
    @staticmethod
    def serialize_individuals(individuals):
        serialized = []
        for ind in individuals:
            serialized.append({
                "genotype": list(ind),  # O vetor binário
                "fitness": list(ind.fitness.values)
            })
        return serialized
    
    @staticmethod
    def deserialize_individuals(serialized_individuals):
        reconstructed = []
        for data in serialized_individuals:
            ind = creator.Individual(data["genotype"])
            ind.fitness.values = tuple(data["fitness"])
            reconstructed.append(ind)
        return reconstructed