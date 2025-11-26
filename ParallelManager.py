import os
import re
from mpi4py import MPI
from deap import creator
from ExperimentEval import ExperimentEval
from ExperimentExec import ExperimentExec

# ====== Constantes de Tags para comunicação ======
TAG_TASK = 1  # A mensagem contém uma tarefa
TAG_RESULT = 2 # A mensagem contém um resultado
TAG_STOP = 0   # Não há mais tarefas (sinal de parada)

DIRETORIO_PATH = os.path.abspath(".outputs")
EXPERIMENTO_PATH = os.path.abspath("./Experimentos")
    
class ParallelManager:    
    def __init__(
        self,
        comm_parallel,
        size_parallel,
        rank_parallel,
        experiments,
        name_test_file,
        class_name_test_file,
        individual_size,
        start_time
        
    ):
        self.comm_parallel = comm_parallel
        self.size_parallel = size_parallel
        self.rank_parallel = rank_parallel
        self.experiments = experiments
        self.name_test_file = name_test_file
        self.class_name_test_file = class_name_test_file
        self.individual_size = individual_size
        self.start_time = start_time
    
    def run(self):
        """Starts the master or slave logic based on the rank."""
        if self.size_parallel < 2:
            print("Erro: Requires at least 2 MPI processes.")
            self.comm_parallel.Abort(1)

        if self.rank_parallel == 0:
            self.master_parallel_loop()
        else:
            print(f"[Slave {self.rank_parallel}] Starting slave loop.")
            self.slave_parallel_loop()
        
            
    def exec_ranking(self):
        print("Mestre: Starting post-processing...")
        experiment_evaluator = ExperimentEval(self.name_test_file, self.class_name_test_file, self.individual_size)
        experiment_evaluator.exec_final_ranking()
    

    def read_best_individuals(self, experiments_folder):
        """
        Lê os arquivos que contenham 'melhores' no nome dentro da pasta experiments_folder,
        reconstrói os indivíduos com genótipo e fitness.
        """
        print(f"[DEBUG][Rank {self.rank_parallel}] Pasta atual: {os.getcwd()}")
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

    def serialize_individuals(self, individuals):
        serialized = []
        for ind in individuals:
            serialized.append({
                "genotype": list(ind),  # O vetor binário
                "fitness": list(ind.fitness.values)
            })
        return serialized
    
    def deserialize_individuals(self, serialized_individuals):
        reconstructed = []
        for data in serialized_individuals:
            ind = creator.Individual(data["genotype"])
            ind.fitness.values = tuple(data["fitness"])
            reconstructed.append(ind)
        return reconstructed
    
    def save_best_individuals(self, individuals, experiment_config):
        file_name = f"seed_{experiment_config.seed}_pop_{experiment_config.pop_size}_gen_{experiment_config.num_gen}_cross_{experiment_config.cross_rate}_muta_{experiment_config.mut_rate}"
        file_name_final = f"Melhores_{file_name}.txt"

        dir_base = experiment_config.output_base_dir
        experiment_folder = f"Experimento_{experiment_config.experiment_count}"
        print("[DEBUG] Diretório base:", dir_base)
        print("[DEBUG] Pasta do experimento:", experiment_folder)
        full_path = os.path.join(dir_base, experiment_folder)

        # Cria diretório se não existir
        os.makedirs(full_path, exist_ok=True)

        caminho_final = os.path.join(full_path, file_name_final)

        with open(caminho_final, "w") as f: 
            for ind in individuals:
                genotype = ind["genotype"]
                fitness = tuple(ind["fitness"])
                f.write(f"Individual('i', {genotype})({fitness})\n")

        print(f"[Mestre] Arquivo '{file_name_final}' salvo em '{full_path}'")
        
    def slave_parallel_loop(self):
        while True:
            status = MPI.Status()
            task_list = self.comm_parallel.recv(source=0, tag=MPI.ANY_TAG, status=status)
            tag = status.Get_tag()

            if tag == TAG_TASK:
                all_serialized = []
                for task_data in task_list:
                    print(f"[Slave {self.rank_parallel}] Executing experiment {task_data.experiment_count}")
                    executor = ExperimentExec(task_data, self.start_time)
                    executor.execute_experiment()
                    
                    experiment_folder_path = os.path.join("./Experimentos", f"Experimento_{task_data.experiment_count}")
                    melhores = self.read_best_individuals(experiment_folder_path)
                    serialized = self.serialize_individuals(melhores)
                    print(f"Escravo {self.rank_parallel}: Enviando resultado para tarefa {task_data}: {serialized}")
                    all_serialized.append({
                        "task_id": task_data.experiment_count,
                        "data": serialized if serialized else {"genotype": [], "fitness": []}
                    })

                # Envia todos os resultados de uma vez
                self.comm_parallel.send({"worker_rank": self.rank_parallel, "result": all_serialized}, dest=0, tag=TAG_RESULT)

            elif tag == TAG_STOP:
                print(f"Escravo {self.rank_parallel}: Recebeu sinal de parada. Encerrando.")
                break
            else:
                print(f"Escravo {self.rank_parallel}: Recebeu tag inesperada {tag}. Ignorando.")

        print(f"Escravo {self.rank_parallel}: Finalizado.")
    
    def master_parallel_loop(self):
        """Master: agenda 1 tarefa por escravo e vai gravando os resultados assim que chegam."""
        tasks = list(self.experiments)
        num_tasks = len(tasks)
        num_workers = self.size_parallel - 1

        if num_workers <= 0 or num_tasks == 0:
            print("[Master] Nada a fazer.")
            return

        print(f"[Master] Dispatching {num_tasks} tasks across {num_workers} workers")

        # Fila de tarefas e mapa para saber qual worker está ocupado
        next_task_idx = 0
        active_workers = set()

        # Dispara uma tarefa por worker (ou até acabarem as tarefas)
        for worker_rank in range(1, self.size_parallel):
            if next_task_idx < num_tasks:
                task = tasks[next_task_idx]
                next_task_idx += 1
                print(f"[Master] Sending 1 task (exp {task.experiment_count}) to slave {worker_rank}")
                # O escravo espera uma LISTA de tarefas — mandamos [task]
                self.comm_parallel.send([task], dest=worker_rank, tag=TAG_TASK)
                active_workers.add(worker_rank)

        # 2) Recebe resultados e, a cada retorno, grava e envia próxima tarefa
        completed = 0
        while completed < num_tasks and active_workers:
            status = MPI.Status()
            try:
                payload = self.comm_parallel.recv(source=MPI.ANY_SOURCE, tag=TAG_RESULT, status=status)
            except Exception as e:
                print(f"[ERRO][Master] Falha recebendo resultado: {e}")
                break

            worker_rank = status.Get_source()
            print(f"[Master] Received result from slave {worker_rank}")

            # payload esperado: {"worker_rank": <int>, "result": [ {task_id, data}, ... ] }
            results_list = payload.get("result", [])
            if isinstance(results_list, dict):
                # defesa: alguns testes podem ter retornado dict em vez de lista
                results_list = [results_list]

            for serialized_ind_data in results_list:
                task_id = serialized_ind_data.get("task_id")
                data = serialized_ind_data.get("data", [])

                # normaliza caso 'data' venha como dict vazio {"genotype":[],"fitness":[]}
                if isinstance(data, dict):
                    # trata como vazio
                    data = []

                try:
                    experiment_config = next(exp for exp in self.experiments if exp.experiment_count == task_id)
                except StopIteration:
                    print(f"[WARN][Master] Experiment config not found for task_id={task_id}. Ignorando.")
                    continue

                print(f"[Master] Writing best individuals for experiment {experiment_config.experiment_count}")
                # IMPORTANTE: não desserializar aqui — save_best_individuals espera dicionários serializados
                self.save_best_individuals(data, experiment_config)

                completed += 1

            # Depois de processar o retorno, se houver mais tarefas, manda a próxima para ESTE worker
            if next_task_idx < num_tasks:
                next_task = tasks[next_task_idx]
                next_task_idx += 1
                print(f"[Master] Sending next task (exp {next_task.experiment_count}) to slave {worker_rank}")
                self.comm_parallel.send([next_task], dest=worker_rank, tag=TAG_TASK)
            else:
                # Sem mais tarefas: sinaliza STOP para este worker e tira da lista de ativos
                print(f"[Master] No more tasks. Sending STOP to slave {worker_rank}")
                self.comm_parallel.send(None, dest=worker_rank, tag=TAG_STOP)
                active_workers.discard(worker_rank)

        # Se por algum motivo sobrou worker ativo (ex.: erro no loop), manda STOP
        for worker_rank in list(active_workers):
            print(f"[Master] Finalizing: sending STOP to slave {worker_rank}")
            self.comm_parallel.send(None, dest=worker_rank, tag=TAG_STOP)

        print(f"[Master] {num_tasks}/{num_tasks} tasks processed.")
        self.exec_ranking()
        print("[Master] Finished.")
