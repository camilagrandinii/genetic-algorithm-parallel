import os
import array
import numpy
import random
from deap import base, tools, creator
from algoritmos_ML import AlgoritmosML
from classificadorT import ClassificadorT


class MOGAToolbox:
    def __init__(
        self,
        INDIVIDUAL_SIZE,
        MUTATION_RATE,
        CLASSIFIER_FILE_NAME,
        CLASSIFIER_PATH,
        SAMPLE_COUNT,
        TAMANHO_TRANSFORMADA,
        arquivo,
        algoritmo_ml,
        SEED,
        diretorio,
        todos_fitness,
        num_geracao
    ):
        self.INDIVIDUAL_SIZE = INDIVIDUAL_SIZE
        self.MUTATION_RATE = MUTATION_RATE
        self.CLASSIFIER_FILE_NAME = CLASSIFIER_FILE_NAME
        self.CLASSIFIER_PATH = CLASSIFIER_PATH
        self.SAMPLE_COUNT = SAMPLE_COUNT
        self.TAMANHO_TRANSFORMADA = TAMANHO_TRANSFORMADA
        # self.DATABASE_PATH = DATABASE_PATH
        self.toolbox = self.setup_and_get_MOGA_toolbox()
        self.arquivo = arquivo
        self.algoritmoML = algoritmo_ml
        self.seed = SEED
        self.diretorio = diretorio
        self.todos_fitness = todos_fitness
        self.num_geracao = num_geracao
        self.model = ClassificadorT()
        self.model.ClassificadorT(self.CLASSIFIER_PATH, self.CLASSIFIER_FILE_NAME)
        

    def setup_creator():
        # O creator cria uma nova classe com o nome passado no parâmetro
        # Em termos mais simples, essa linha de código cria uma nova classe de aptidão chamada FitnessMulti que tem dois componentes.
        # O primeiro componente é positivo e o segundo componente é negativo. A biblioteca Deap irá minimizar o segundo componente
        # da aptidão, o que significa maximizar o primeiro componente da aptidão.
        # O creator cria uma nova classe com o nome passado no parâmetro
        if "FitnessMulti" not in creator.__dict__:
            creator.create("FitnessMulti", base.Fitness, weights=(1.0, -1.0))
        if "Individual" not in creator.__dict__:
            # array.array -> é usado para criar um arranjo de tipos específicos.
            # no caso o Type code é i, logo ele cria um arranjo de inteiros
            # Ele cria um arranjo com os elementos do fitnes.
            creator.create(
                "Individual", array.array, typecode="i", fitness=creator.FitnessMulti
            )
        
    def setup_and_get_MOGA_toolbox(self):
        # Attribute generator
        toolbox = base.Toolbox()

        # O método register registra uma função na biblioteca Deap com o nome passado e você pode fornecer argumentos padrão que serão passados ​​automaticamente
        # ao chamar a função registrada. Argumentos fixos podem então ser substituídos no momento da chamada da função.

        # Em específico essa função gera uma função que quando chamada ela gera números aleatórios entre 1 e 0;
        toolbox.register("indices", random.randint, 0, 1)

        # A função tools.initRepeat repete um procedimento uma quantidade específica de vezes, no caso abaixo
        # seria a quantidade de vezes do IND_SIZE.
        # Essa função registra um indivíduo e inicializa ele com 0s - 1s aleatórios e repete IND_SIZE vezes.
        toolbox.register("individual",tools.initRepeat,creator.Individual,toolbox.indices,self.INDIVIDUAL_SIZE)

        # Essa função registra uma função de colocar indivíduos em uma lista e repete toolbox.individual vezes
        # (quantidade de indivíduos).
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        # Operadores genetic
        # registra uma função de seleção de indivíduo do NSGA2
        toolbox.register("select", tools.selNSGA2)

        # registra uma função que executa um cruzamento de dois pontos nos indivíduos da sequência de entrada
        toolbox.register("mate", tools.cxTwoPoint)

        # registra uma função que embaralhe os atributos do indivíduo de entrada e retorne o mutante.
        toolbox.register("mutate", tools.mutShuffleIndexes, indpb=self.MUTATION_RATE)

        # registra a função criada evaluate na biblioteca Deap
        toolbox.register("evaluate", self.evaluate_fitness_of_individual)

        # faz o cruzemento entre pais, gera os filhos e armazena pai e filho juntos
        toolbox.decorate("mate", self.mate_and_get_mating_info)
        # toolbox.register("map", dtm.map)

        return toolbox

    def evaluate_fitness_of_individual(self, individual): # type: ignore
        """Essa função retorna o fitness do indivíduo.

        Args:
            individual : creator.Individual
                indivíduos da população.

        Returns:
            (float64, int)
                o fitness para o indivíduo e a quantidade de características.
        """
        # dentro do cromossomo temos as características presentes no indivíduos [0,1,0,1,0,1]
        # ele pega esses atributos e dentro de um svm ele testa para ver a qualidade dele.
        attributes_of_individual = self.get_attributes_of_individual(individual)
        # print(attributes_of_individual)
        self.create_file(individual)
        fitness = self.get_fitness_of_individual(self.algoritmoML,attributes_of_individual)
        # check whether this comment is really useful or not
        # fitness = 1 - fitness
        individual_size = (attributes_of_individual.__len__())
        str_fitness =  (str(individual) + " " + str(fitness))
        self.todos_fitness.append(str_fitness)
        return fitness, individual_size

    def get_fitness_of_individual(self, algoritmoML, attribute_list) -> numpy.float64: # type: ignore
        """_summary_ Recebe uma lista de caracteristicas de apenas 1 indivíduo.

        Args:
            listaCaracteristicas (_type_): lista com 0s e 1s [0,1,0,1] -> Cromossomo.

        Returns:
            _type_: Como o fitness no trabalho do Bruno é baseado no fmeasure ele retorna o fmeasure.
        """

        if not attribute_list:
            _FMeasure_result = 0
        else:
            _FMeasure_result = self.model.fitness(algoritmoML, self.arquivo, self.num_geracao)
        return _FMeasure_result

    def get_attributes_of_individual(self, individual) -> [str]: # type: ignore
        """Lista as características (atributos) de um indivíduo.
        Pega somente as "Colunas" onde temos o 1.

        Args:
            individual : deap.creator.Individual
                o indivíduo. (cromossomo [0,0,1,0,...]).

        Returns:
            [str]
                lista com as caracterísitcas do indivíduo.
        """
        attributes = []
        attribute_count = 0
        
        for attribute in individual:
            if attribute == 1:
                attributes.append(attribute_count) 
            attribute_count += 1
        return attributes

    def create_file(self, attributes_of_individual): 
        """_summary_ Gera um arquivo igual uma base de dados para testar na svm

        Args:
            attributes_of_individual : [str]
                Quantidade listada de características, igual quando faz leitura em um csv
        """
        nome_arquivo = "Log_" + self.seed + str(self.num_geracao)
        nome_diretorio = self.diretorio.constroi_caminho(self.diretorio.get_path(), nome_arquivo)
        SVM_FILE = open(nome_diretorio, "w")
        self.arquivo.arquivo_csv(self.SAMPLE_COUNT, attributes_of_individual, self.TAMANHO_TRANSFORMADA)
        self.arquivo.monta_csv(SVM_FILE)
        # print("algo")
        SVM_FILE.close()
        
    
    # Em termos simples, o decorador mate_decorator() permite que você armazene os pais dos filhos gerados
    # por um cruzamento. Isso pode ser útil para fins de depuração ou para rastrear a evolução de uma
    # população ao longo do tempo.
    def mate_and_get_mating_info(self, mating_function: callable) -> callable:
        def wrapper(parent_1, parent_2, *args, **kwargs):
            parent_fitness_values = []
            for parent in (parent_1, parent_2):
                parent_fitness_values.append(parent.fitness.values)
            offspring = mating_function(parent_1, parent_2, *args, **kwargs)
            result = offspring
            for child in offspring:
                child.parents = parent_fitness_values
            return result

        return wrapper

