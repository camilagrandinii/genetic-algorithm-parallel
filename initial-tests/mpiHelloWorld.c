#include <mpi.h>
#include <stdio.h>

int main(int argc, char** argv) {
    MPI_Init(NULL, NULL);

    int world_rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &world_rank); // pega o rank (ID) do processo
    int world_size;
    MPI_Comm_size(MPI_COMM_WORLD, &world_size); // pega número total de processos

    printf("Hello from process %d out of %d\n", world_rank, world_size);

    MPI_Finalize();
    return 0;
}
