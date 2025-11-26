import os
import sys
import pandas as pd
# Pega o diretório onde o arquivo Classificador está alocado.
sys.path.insert(0, '../codigos_AG')

class Arquivo:

    def __init__(self):
        self.numero_amostras = None
        self.lista_classes = None
        self.tamanho_transformada = None
        self.arquivo = None
        self.dataset_clone = None

    def set_nome_classe_arquivo_teste(self, nome_classe_arquivo_teste):
        self.nome_classe_arquivo_teste = nome_classe_arquivo_teste

    def get_nome_classe_arquivo_teste(self):
        return self.nome_classe_arquivo_teste

    def le_arquivo_teste(self):
        with open("teste.txt", "r") as file:
            linhas_arquivo = file.readlines()
            
        file.close()
        return linhas_arquivo
            
    

    def le_arquivo(self, nomeArquivo):
        if '.csv' not in nomeArquivo:
            print('Por favor envie um arquivo do tipo csv')

        self.localArquivo = os.path.join(nomeArquivo)
        self.dataset = pd.read_csv(self.localArquivo)
        self.dataset_clone = self.dataset
        # pega o nome dos atributos.
        self.atributos = self.dataset.columns.to_list()

    def le_arquivo_txt(nomeArquivo):
        with open(nomeArquivo, mode='r')as f:
            arquivo = f.read()
            f.close()
        return arquivo
    
    def escreve_arquivo_backup(nome_arquivo, linha):
        with open(nome_arquivo, mode='w') as f:
            f.write(linha)
            f.close()

    def retorna_nome_atributos(self):
        return self.atributos
    
    def retorna_dataset(self):
        return self.dataset

    def quantidade_linhas_colunas(self, operador):

        if operador == 1:
            resposta = self.dataset.shape[1]  # pega a quantidade de colunas
        elif operador == 0:
            resposta = self.dataset.shape[0]  # pega a quantidade de linhas
            resposta = resposta.__str__()

        return resposta

    def arquivo_csv(self, numero_amostras, lista_classes, tamanho_transformada):
        self.numero_amostras = numero_amostras
        self.lista_classes = lista_classes
        self.tamanho_transformada = tamanho_transformada
        self.arquivo = ""

    def monta_csv(self, arquivo_saida):
        # print(self.lista_classes)
        # print(type(self.numero_amostras))
        dataset, classe = self.dataframe_to_csv_test(self.lista_classes)
        dataframe = pd.concat([dataset,classe], axis=1)
        arquivo_saida.close()

        # print(arquivo_saida.name)
        # a variável index recebe os índices e a row recebe as linhas
        with open(arquivo_saida.name, 'a') as f:
            for index, row in dataframe.iterrows():
                linha = ', '.join(row.astype(str))
                f.write(f"{linha}\n")

    def dataframe_to_csv_test(self, atributos_ind):
        # print(atributos_ind)
        dataset, classe = self.prepara_data_frame(self.nome_classe_arquivo_teste)
        # print(dataset)
        # pega as colunas que tem 1
        cols_para_manter = [dataset.columns[i] for i in range(len(dataset.columns)) if atributos_ind[i] != 0]
        dataset = dataset[cols_para_manter]
        return dataset, classe

    def dataframe_to_csv_test_econtra_melhor(self, atributos_ind, nome_class):
        # print(atributos_ind)
        dataset, classe = self.prepara_data_frame(nome_class)
        # print(dataset)
        # pega as colunas que tem 1
        cols_para_manter = [dataset.columns[i] for i in range(len(dataset.columns)) if atributos_ind[i] != 0]
        dataset = dataset[cols_para_manter]
        return dataset, classe


    def prepara_data_frame(self, nomeClass):
        dataset = self.dataset_clone

        # A ideia é que o usuário informe o nome da classe ou simplesmente pegamos a última coluna.
        if "class" in nomeClass:
            # print("entrei aqui_1")
            # pego a última coluna e removo ela!
            nome_ultima_coluna = dataset.columns[dataset.columns.__len__()-1]
            classe = dataset[nome_ultima_coluna]
            dataset = dataset.drop(nome_ultima_coluna, axis=1)
        else:
            # print("entrei aqui_2")
            classe = dataset[nomeClass]
            dataset = dataset.drop(nomeClass, axis=1)
        # dataset=dataset.drop(dataset.index[0])
        # print(dataset)
        return dataset, classe

    def dataSet(self):
        return self.dataset

    def classes(self):
        classes = self.dataset.columns
        return classes

    def retorna_quantidade_colunas(self):
        dataset, _ = self.prepara_data_frame(self.nome_classe_arquivo_teste)
        num_colunas = len(dataset.columns)
        return num_colunas
    
    def encontrar_arquivo(pasta, nome_arquivo):
        # print(pasta)
        caminho = []
        experimentos = []
        # Percorre todos os arquivos na pasta
        for root, dirs, files in os.walk(pasta):
            # print("passei aqui"+str(files))
            for file in files:
                # Verifica se o nome do arquivo corresponde ao nome procurado
                if file.startswith(nome_arquivo):
                    caminho.append(str(os.path.join(root, file)))
            experimentos.append(caminho)
        return experimentos
