from sklearn import tree
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier

class AlgoritmosML:

    def __init__(self, nome_classificador, lista_parametros):
        self.nome_classificador = nome_classificador
        parametros = self.monta_tupla(lista_parametros)

        if nome_classificador == "SVM":
            self.modelo = self.SVM(**parametros)
        elif nome_classificador == "KNN":
            self.modelo = self.KNN(**parametros)
        elif nome_classificador == "DecisionTree":
            self.modelo = self.DecisionTree(**parametros)
        else:
            raise ValueError(f"Classificador desconhecido: {nome_classificador}")

    def monta_tupla(self, lista_parametros):
        parametros_dict = {}
        for param in lista_parametros[1:]:
            if ':' in param:
                chave, valor = param.split(':', 1)
                # Converte os valores para os tipos apropriados
                if valor.lower() in ('true', 'false'):
                    valor = valor.lower() == 'true'
                elif valor == 'None':
                    valor = None
                elif valor.isdigit():
                    valor = int(valor)
                else:
                    try:
                        valor = float(valor)
                    except ValueError:
                        pass
                parametros_dict[chave] = valor
        return parametros_dict

    def KNN(self, **kwargs):
        return KNeighborsClassifier(**kwargs)

    def SVM(self, **kwargs):
        return SVC(**kwargs)

    def DecisionTree(self, **kwargs):
        return tree.DecisionTreeClassifier(**kwargs)

    def get_model(self):
        return self.modelo
