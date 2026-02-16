# Parallel Genetic Algorithm with MPI — TCC Project

This repository contains the source code developed for the Undergraduate Thesis (TCC) on the parallelization of a Genetic Algorithm (NSGA-II for feature selection) using MPI (Message Passing Interface).

The project allows distributed execution on a cluster, speeding up evolutionary processing by dividing evaluations among different MPI processes.

---

## 📥 Cloning the Repository

Clone the repository using:

```bash
git clone git@github.com:camilagrandinii/genetic-algorithm-parallel.git
```

Navigate to the directory:
```bash
cd genetic-algorithm-parallel
```

## Prerequisites
Before running the experiments, make sure you have:
- MPI (Message Passing Interface) support
Ex.: openmpi
- Python 3.x
- All project dependencies installed (via requirements.txt)
- A machine with multiple cores or a properly configured computer cluster
- Passwordless SSH access between the master node and the worker nodes
- All nodes correctly configured in the file:
  
```bash
/etc/hosts
```

## SSH Configuration
- Passwordless authentication is essential to allow mpirun to automatically distribute processes among remote nodes.

### Generate Keys
```bash
ssh-keygen -t rsa
```

### Copy the Public Key to Each Participating Node
```bash
ssh-copy-id usuario@nome_do_no
```

Repeat this process for all cluster nodes.

## Configuration of Required Files

- /etc/hosts

This file defines how each machine in the cluster identifies the others.

A working example:

```bash
127.0.0.1 localhost
127.0.1.1 PMG34MIFLB21210
10.160.0.100 servidorSubordinado1
10.160.0.101 servidorSubordinado2

# IPv6
::1     ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters

Sem esta configuração, você pode encontrar:
  - Erros de Conexão via MPI
  - Lentidão na comnuicação
  - Falhas ou timeouts ao iniciar processos remotos
```

- mpi_hosts

Defines the participant nodes and how many MPI processes each node can receive (slots):

```bash
master slots=1
servidorSubordinado1 slots=2
servidorSubordinado2 slots=2
```

In this example, the cluster has 5 slots.
Thus, in it's execution we can use: 

```bash
-np 5
```

- teste.txt

FIle with all the hyperparameters of the genetic algorithm and dataset definition.

```bash
dataset_balanceado_final.csv classe
1 backup_geracao.txt
seed 2156 2 885463215
Population 204 504 200
Generations 200 504 200
CrossOverFactor 0.7 0.91 0.2
TournamentSize 2
MutationRate 0.1 0.41 0.2
ElitismFactor 1
DecisionTree  max_depth=5
```

Configures:
  - Dataset name
  - Target class
  - Seeds
  - Population and generation intervals
  - Mutation and crossover rates
  - Maximum depth of the decision tree used in evaluation

This file must be adapted according to each experiment.

## Running the Code

After configuring mpi_hosts, /etc/hosts, and passwordless SSH:

Execute:

```bash
mpirun --hostfile mpi_hosts -np [NUM_PROCESSOS] python main.py teste.txt
```

Example with 5 slots:

```bash
mpirun --hostfile mpi_hosts -np 5 python main.py teste.txt
```

## Important Notes
Correct configuration of the mpi_hosts, teste.txt, and /etc/hosts files is essential.
Passwordless SSH must work perfectly before using MPI.
If any node is inaccessible, mpirun will fail to start the execution.
All nodes must have Python and project dependencies installed.

## 📄 Licença
This repository is provided under the terms of use of the LICAP laboratory.
This means you are allowed to use, copy, modify, merge, publish, distribute, and sell the software, as long as you retain the original copyright notice and a copy of the license in any redistribution.
