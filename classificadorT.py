import sys
import pickle
import numpy as np
from sklearn.base import clone, clone
from sklearn.model_selection import KFold, cross_val_score
from sklearn.metrics import f1_score, make_scorer, recall_score, accuracy_score, precision_score, confusion_matrix, classification_report


class ClassificadorT:

    num_geracao = 0

    def __init__(self) -> None:
        pass

    def ClassificadorT(self, path, nomeArquivo):
        self.path = path
        self.nomeArquivo = nomeArquivo

    def set_num_geracao(self, num_geracao):
        ClassificadorT.num_geracao = num_geracao

    def evaluate_model_with_cross_validation(self, model, X_rus, y_rus, cv=10, scoring='accuracy'):    
        melhor = 0
        labels = ['1', '2']  # respostas
        modelos = []
        
        # Definir os scorers
        scorers = {
            'accuracy': make_scorer(accuracy_score),
            'f1_score': make_scorer(f1_score, average='weighted', zero_division=1),  # zero_division=1 para F1-score
            'recall': make_scorer(recall_score, average='weighted', zero_division=1),  # zero_division=1 para Recall
            'precision': make_scorer(precision_score, average='weighted', zero_division=1)  # zero_division=1 para Precisão
        }
        
        # Preparar validação cruzada
        kf = KFold(n_splits=cv)
        
        # Inicializar listas para armazenar os resultados
        results = []
        
        # Realizar a validação cruzada
        for fold, (train_index, test_index) in enumerate(kf.split(X_rus, y_rus), 1):
            X_train, X_test = X_rus.iloc[train_index], X_rus.iloc[test_index]
            y_train, y_test = y_rus.iloc[train_index], y_rus.iloc[test_index]
            
            # Clonar o modelo para evitar o ajuste acumulativo
            cloned_model = clone(model)
            
            # Treinar o modelo
            cloned_model.fit(X_train, y_train)

            # Armazenar os modelos
            modelos.append(cloned_model)
            # Calcular as métricas no conjunto de treino
            y_pred_train = cloned_model.predict(X_train)
            
            # Calcular as métricas no conjunto de treino
            accuracy = accuracy_score(y_train, y_pred_train)
            f1 = f1_score(y_train, y_pred_train, average='weighted', zero_division=1)
            recall = recall_score(y_train, y_pred_train, average='weighted', zero_division=1)
            precision = precision_score(y_train, y_pred_train, average='weighted', zero_division=1)
            
            # Armazenar a matriz de confusão e o relatório de classificação
            cm = confusion_matrix(y_train, y_pred_train)
            cr = classification_report(y_train, y_pred_train, target_names=labels)
            
            # Armazenar os resultados formatados
            fold_result = {
                'fold': fold,
                'accuracy': accuracy,
                'f1_score': f1,
                'recall': recall,
                'precision': precision,
                'confusion_matrix': cm,
                'classification_report': cr
            }
            
            results.append(fold_result)
        
        f1_scores = [result['f1_score'] for result in results]

        aux = 0
        id_melhor_modelo = 0

        for i, j in enumerate(f1_scores):
            if aux < j:
                aux = j
                id_melhor_modelo = i
        
        best_model = modelos[id_melhor_modelo]
        best_score = aux        
        return best_score, best_model

    def selec_best_model(self, model, score):
        with open("best_score_crossvalidation.txt", 'r') as file:
            line = file.readline()
        if(line == '0000'):
            with open("best_score_crossvalidation.txt", 'w') as file:    
                file.write(str(score))
            with open('modelo_treinado.pkl', 'wb') as file:
                pickle.dump(model, file)
        elif float(line) < score:
            with open("best_score_crossvalidation.txt", 'w') as file:    
                file.write(str(score))
                with open('modelo_treinado.pkl', 'wb') as file:
                    pickle.dump(model, file)


    #receber a variável arquivo
    def fitness(self, algoritmoML, arquivo, num_geracao):
        aux = 0
        dataset, classe = arquivo.prepara_data_frame(arquivo.get_nome_classe_arquivo_teste())
        score = cross_val_score(algoritmoML, dataset, classe, cv=10, scoring='f1_macro')

        return score.mean()

    # def fitness(self, algoritmoML, arquivo, num_geracao):
    #     aux = 0
    #     dataset, classe = arquivo.prepara_data_frame(arquivo.get_nome_classe_arquivo_teste())

    #     if (ClassificadorT.num_geracao < (int(num_geracao)-1)):
    #         f1_score = cross_val_score(algoritmoML, dataset, classe, cv=10, scoring='f1_macro')
    #         for i in f1_score:
    #             if aux < i:
    #                 aux = i
    #         score = aux
    #     else:
    #         score, model = self.evaluate_model_with_cross_validation(algoritmoML, dataset, classe, cv=10, scoring='f1_score')
    #         self.selec_best_model(model, score)


    #     return score 


