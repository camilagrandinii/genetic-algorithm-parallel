import os
from Arquivo import Arquivo
from diretorio import Diretorio
from rankeamento import Rankeamento
from encontra_melhor import Encontra_melhor
from valida import valida_experimento

DIRETORIO_PATH = os.path.abspath(".outputs")
EXPERIMENTO_PATH_ = os.path.abspath("./Experimentos")
RESULTADOS_PATH = os.path.abspath("./Resultados_teste")

class ExperimentEval:
    def __init__(self,
                 name_test_file,
                 class_name_test_file,
                 individual_size):
        self.name_test_file = name_test_file
        self.class_name_test_file = class_name_test_file
        self.individual_size = individual_size
        
    def exec_final_ranking(self):
        print("[DEBUG] Conteúdo de EXPERIMENTO_PATH_:", os.listdir(EXPERIMENTO_PATH_))
        print("[DEBUG] Conteúdo de DIRETORIO_PATH:", os.listdir(DIRETORIO_PATH))
        print("[DEBUG] Conteúdo de RESULTADOS_PATH:", os.listdir(RESULTADOS_PATH))
        rank = Rankeamento()
        arquivo = Arquivo()
        arquivo.le_arquivo(self.name_test_file)    
        arquivo.set_nome_classe_arquivo_teste(self.class_name_test_file)
        diretorio = Diretorio(DIRETORIO_PATH)
        diretorio.remove_arquivos(RESULTADOS_PATH)
        
        conteudo = os.listdir("./Experimentos")
        if not conteudo:
            print("[ERRO] Nenhum arquivo salvo em ./Experimentos. Não posso fazer ranking.")
            return
        
        print("Experiment path:", EXPERIMENTO_PATH_)
        print("\nResultados path:", RESULTADOS_PATH)
        rank.junta_arquivos(EXPERIMENTO_PATH_, RESULTADOS_PATH)
        colunas = rank.processa_arquivos_teste(EXPERIMENTO_PATH_, RESULTADOS_PATH, self.individual_size)
        colunas_para_filtrar = [item[0] for item in colunas]  
        colunas_tratadas = [int(coluna.split(" ")[-1].strip()) for coluna in colunas_para_filtrar]
        validacao = valida_experimento()
        dataset = arquivo.retorna_dataset()
        validacao.valida_sem_salvar_modelo(dataset, self.class_name_test_file, colunas_tratadas)
        melhor_individuo = Encontra_melhor()
        lista_individuos = melhor_individuo.encontra_melhores_individuos(RESULTADOS_PATH)
        resultados = melhor_individuo.avalia_individuos(arquivo, lista_individuos, self.class_name_test_file)
        resultados.sort(key=lambda x: x['f1_score'], reverse=True)
        print("\nMelhor indivíduo encontrado:")
        print(f"F1-score: {resultados[0]['f1_score']:.4f}")
        print(f"Qtd atributos: {resultados[0]['qtd_atributos']}")
        print(f"Atributos selecionados: {resultados[0]['nomes_colunas']}")