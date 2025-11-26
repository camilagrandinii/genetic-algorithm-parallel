import os
import re
import shutil


class Rankeamento:
    def processa_arquivos_teste(self, diretorio_teste, diretorio_resultados, quantidade_columns):
        individuos = []
        # pega a quantidade de colunas menos a classe.
        # print(quantidade_columns)
        colunas = [0] * (int(quantidade_columns)) 

        self.junta_arquivos(diretorio_resultados, diretorio_teste)

        for root, dirs, files in os.walk(diretorio_resultados):
            for file in files:
                if file.endswith('.txt'):  # ou a extensão que seus arquivos usam
                    caminho_arquivo = os.path.join(root, file)
                    with open(caminho_arquivo, 'r') as f:
                        for indice_linha, linha in enumerate(f, start=1):
                            # Extrair os valores entre colchetes usando expressão regular
                            match = re.search(r'\[(.*?)\]', linha)
                            if match:
                                individuo = list(map(int, match.group(1).split(',')))
                                individuos.append(individuo)

        

        # Atualiza a contagem de 1's em cada coluna
        for i in individuos:
            for j, k in enumerate(i):
                if k == 1:
                    colunas[j] += 1

        # Cria uma lista de tuplas (coluna, quantidade de 1's)
        colunas_com_contagem = [(f"Coluna {idx}", count) for idx, count in enumerate(colunas)]

        # Ordena a lista de tuplas com base na contagem (ordem decrescente)
        colunas_ordenadas = sorted(colunas_com_contagem, key=lambda x: x[1], reverse=True)

        # Imprime as colunas e suas quantidades de 1's, ordenadas
        print("\nContagens ordenadas das colunas (decrescente):")
        for coluna, count in colunas_ordenadas:
            print(f"{coluna}: {count}")
            
        return colunas_ordenadas

    def junta_arquivos (self, diretorio_testes, diretorio_resultados):
        os.makedirs(diretorio_resultados, exist_ok=True)
        
        for subpasta in os.listdir(diretorio_testes):
            subpasta_caminho = os.path.join(diretorio_testes, subpasta)
            
            if os.path.isdir(subpasta_caminho):
                for arquivo in os.listdir(subpasta_caminho):
                    arquivo_caminho = os.path.join(subpasta_caminho,arquivo)
                    if os.path.isfile(arquivo_caminho):
                        shutil.copy(arquivo_caminho, diretorio_resultados)
                        
        
        