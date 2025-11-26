import os
import re
from Arquivo import Arquivo
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score


class Encontra_melhor:
    def encontra_melhores_individuos(self,diretorio_resultados):
        print("Encontrando melhores individuos...")
        lista_individuos = []

        for root, dirs, files in os.walk(diretorio_resultados):
            for file in files:
                if file.endswith('.txt') and 'Melhores' in file:
                    caminho_arquivo = os.path.join(root, file)
                    with open(caminho_arquivo, 'r') as f:
                        for linha in f:
                            match = re.search(r"Individual\('i',\s*\[(.*?)\]\)", linha)
                            if match:
                                bits = list(map(int, match.group(1).split(',')))
                                lista_individuos.append({
                                                            'atributos': bits,
                                                            'origem': file
                                                        })
        
        return lista_individuos

    def avalia_individuos(self, arquivo, lista_individuos, nome_class):
        resultados = []

        print("Avaliando melhores individuos...")

        colunas_dataset = arquivo.dataset_clone.drop(nome_class, axis=1).columns.tolist()

        for info in lista_individuos:
            individuo = info['atributos']
            nome_arquivo = info['origem']

            X, y = arquivo.dataframe_to_csv_test_econtra_melhor(individuo, nome_class)

            clf = DecisionTreeClassifier(max_depth=5)
            scores = cross_val_score(clf, X, y, cv=10, scoring='f1_macro')

            media_f1 = scores.mean()
            qtd_atributos = sum(individuo)

            nomes_colunas = [nome for nome, flag in zip(colunas_dataset, individuo) if flag == 1]

            resultados.append({
                'atributos': individuo,
                'qtd_atributos': qtd_atributos,
                'f1_score': media_f1,
                'nomes_colunas': nomes_colunas,
                'arquivo_origem': nome_arquivo  # <- anexa o nome do arquivo aqui
            })

        return resultados

# def main():
#     arquivo = Arquivo()
#     arquivo.le_arquivo("BaseHipertensao.csv")

#     nome_class = 'diagnostico_hipertensao'
#     diretorio_resultados = './Resultados_teste'
#     lista_individuos = encontra_melhores_individuos(diretorio_resultados)
#     resultados = avalia_individuos(arquivo, lista_individuos, nome_class)

#     resultados.sort(key=lambda x: x['f1_score'], reverse=True)
#     print("\nMelhor indivíduo encontrado:")
#     print(f"F1-score: {resultados[0]['f1_score']:.4f}")
#     print(f"Qtd atributos: {resultados[0]['qtd_atributos']}")
#     print(f"Atributos selecionados: {resultados[0]['nomes_colunas']}")
#     print(f"Arquivo de origem: {resultados[0]['arquivo_origem']}")

# if __name__ == "__main__":
#     main()
