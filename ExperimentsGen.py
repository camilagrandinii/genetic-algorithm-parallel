import os
from Arquivo import Arquivo
from ExperimentConfig import ExperimentConfig
from utils.ParamsExtracter import ParamsExtracter

CLASSIFIER_PATH = os.path.abspath("Individuos")
DIRETORIO_PATH = os.path.abspath("Experimentos")

class ExperimentsGen:
    """
    Classe para gerar combinações de parâmetros de experimentos,
    com suporte para retomar a partir de um ponto de backup.
    """
    def __init__(
        self,
        individual_size,
        sample_count,
        seeds, # Lista de seeds (strings ou ints)
        pop_sizes, # np.arange ou lista de tamanhos de população
        num_gens, # np.arange ou lista de números de gerações
        cross_rates, # np.arange ou lista de taxas de cruzamento
        mut_rates, # np.arange ou lista de taxas de mutação
        backup_parameters,
        tournament_size,
        classifier_name,
        ml_model_params,
        name_test_file,
        name_class_test_file
    ):
        """
        Inicializa com as listas ou ranges de parâmetros a serem combinados.
        """
        self.seeds = seeds
        self.pop_sizes = pop_sizes
        self.num_gens = num_gens
        self.cross_rates = cross_rates
        self.mut_rates = mut_rates
        self.backup_parameters = backup_parameters
        self.individual_size = individual_size
        self.sample_count = sample_count
        self.tournament_size = tournament_size
        self.classifier_name = classifier_name
        self.ml_model_params = ml_model_params
        self.name_test_file = name_test_file
        self.class_name_test_file = name_class_test_file
        
    def generate_all_experiments(self, backup) -> list:
        params_extracter = ParamsExtracter()
        retomar = int(backup[0]) == 0

        if retomar:
            backup_data = params_extracter.parse_backup_file(backup[1])
            resume_params = {
                'seed': backup_data["seed"],
                'pop_size': backup_data["pop"],
                'num_gen': backup_data["gen"],
                'cross_rate': backup_data["cross"],
                'mut_rate': backup_data["mut"]
            }
            start_count = backup_data["contador"]
            print(f"[Main] Retomando a partir do backup: {resume_params}, contador = {start_count}")
            return self.get_experiments_to_run(resume_params, start_count=start_count)

        print("[Main] Executando todos os experimentos do zero.")
        return self.get_experiments_to_run()

    def get_experiments_to_run(self, resume_params=None, start_count=0):
        """
        Gera a lista de dicionários de parâmetros para os experimentos
        que ainda precisam ser executados, pulando os já concluídos
        com base nos parâmetros de retomada.

        Args:
            resume_params (dict, optional): Dicionário contendo os parâmetros
                do último experimento concluído com sucesso (ou o próximo a ser
                executado se a interrupção foi antes do início). 
                Ex: {'seed': '123', 'pop_size': 100, 'num_gen': 50, 
                     'cross_rate': 0.8, 'mut_rate': 0.1}. 
                Defaults to None (executa todos desde o início).
            start_count (int, optional): O valor inicial para o contador 
                do experimento, geralmente lido do backup. Defaults to 0.

        Returns:
            list: Lista de dicionários, onde cada dicionário representa os
                  parâmetros de um experimento a ser executado.
        """
        experiment_parameters = []
        current_count = start_count
        
        # Determina se precisamos pular experimentos
        skip = bool(resume_params) 
        
        print(f"Gerando experimentos a partir do contador: {start_count}")
        if skip:
            print(f"Tentando retomar após: {resume_params}")

        for seed_val in self.seeds:
            # Converte para string para comparação consistente, se necessário
            current_seed_str = str(seed_val) 
            for pop_size in self.pop_sizes:
                # Ignora pop_size não divisível por 4, como no original
                if pop_size % 4 != 0:
                    continue
                for num_gen in self.num_gens:
                    for cross_rate in self.cross_rates:
                        current_cross_rate = round(cross_rate, 3)
                        for mut_rate in self.mut_rates:
                            current_mut_rate = round(mut_rate, 3)

                            if skip:
                                # Compara os parâmetros atuais com os de retomada
                                # Certifique-se que os tipos são comparáveis (str vs str, int vs int, float vs float)
                                if (
                                    current_seed_str == str(resume_params.get('seed')) and
                                    int(pop_size) == int(resume_params.get('pop_size')) and
                                    int(num_gen) == int(resume_params.get('num_gen')) and
                                    current_cross_rate == round(resume_params['cross_rate'], 3) and
                                    current_mut_rate == round(resume_params['mut_rate'], 3)
                                ):
                                    print(f"Ponto de retomada encontrado em {resume_params}. Retomando a execução.")
                                    skip = False
                                    # A partir daqui, executa os experimentos
                                    # Não faz `continue` aqui, pois queremos executar este experimento
                                else:
                                    # Ainda não chegou no ponto de retomada, continua pulando
                                    continue 

                            # Se skip é False
                            # Adiciona os parâmetros do experimento atual à lista
                            
                            experiment_params = ExperimentConfig(seed_val, 
                                                                int(pop_size), 
                                                                int(num_gen),
                                                                current_cross_rate,
                                                                current_mut_rate,
                                                                current_count,
                                                                self.individual_size,
                                                                self.sample_count,
                                                                CLASSIFIER_PATH,
                                                                self.tournament_size,
                                                                self.name_test_file,
                                                                self.class_name_test_file,
                                                                self.classifier_name,
                                                                self.ml_model_params,
                                                                DIRETORIO_PATH
                                                                )
                            experiment_parameters.append(experiment_params)
                            parametros = f"i:{seed_val}\nj:{pop_size}\nk:{num_gen}\nl:{cross_rate}\nm:{mut_rate}\ncontador:{current_count}"
                            Arquivo.escreve_arquivo_backup(self.backup_parameters[1], parametros)
                            
                            # Incrementa o contador para o próximo experimento
                            current_count += 1
                            
        if resume_params and skip:
             print("Aviso: Ponto de retomada especificado não foi encontrado na combinação de parâmetros.")

        print(f"Total de {len(experiment_parameters)} experimentos adicionados para execução.")
        return experiment_parameters

