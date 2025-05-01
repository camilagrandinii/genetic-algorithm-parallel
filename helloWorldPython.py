from mpi4py import MPI

# Inicializa o ambiente MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()  # Obtém o rank (ID) do processo
size = comm.Get_size()  # Obtém o número total de processos
processor_name = MPI.Get_processor_name()  # Obtém o nome do processador

print(f"Hello from process {rank} out of {size} on {processor_name}")

# Finaliza o ambiente MPI (não é necessário explicitamente em mpi4py, mas bom para clareza)
MPI.Finalize()
