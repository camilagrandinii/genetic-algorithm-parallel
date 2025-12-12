# Algoritmo Genético Paralelo com MPI — Projeto de TCC

Este repositório contém o código-fonte desenvolvido para o Trabalho de Conclusão de Curso (TCC) da paralelização de Algoritmos Genético (NSGA-II para seleção de atributos) utilizando MPI (Message Passing Interface).

O projeto permite execução distribuída em cluster, acelerando o processamento evolutivo pela divisão das avaliações entre diferentes processos MPI.

---

## 📥 Clonando o Repositório

Clone o repositório utilizando:

```bash
git clone git@github.com:camilagrandinii/genetic-algorithm-parallel.git
```

Acesse o diretório:
```bash
cd genetic-algorithm-parallel
```
## Pré-Requisitos
Antes de executar os experimentos, certifique-se de possuir:
- Suporte a MPI (Message Passing Interface)
Ex.: openmpi
- Python 3.x
- Todas as dependências do projeto instaladas (arquivo requirements.txt)
- Máquina com múltiplos núcleos ou um cluster de computadores configurado
- Acesso SSH sem senha entre o nó master e os nós subordinados
- Todos os nós configurados corretamente no arquivo:
  
```bash
/etc/hosts
```

## Configuração do SSH
- A autenticação sem senha é essencial para permitir que o mpirun distribua processos entre nós remotos automaticamente.

### Gere as Chaves
```bash
ssh-keygen -t rsa
```

### Copie a chave pública para cada nó participante
```bash
ssh-copy-id usuario@nome_do_no
```

Repita esse processo para todos os nós do cluster.

## Configuração dos Arquivos Necessários

- /etc/hosts

  Este arquivo define como cada máquina do cluster identifica as demais.

  Um exemplo funcional:

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

Define os nós participantes e quantos processos MPI cada nó pode receber (slots):

```bash
master slots=1
servidorSubordinado1 slots=2
servidorSubordinado2 slots=2
```

Neste exemplo, o cluster possui 5 slots.
Ou seja, sua execução pode usar: 

```bash
-np 5
```

- teste.txt

Arquivo com os parâmetros do algoritmo genético e definição do dataset.

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

Configura:
  - Nome do dataset
  - Classe alvo
  - Seeds
  - Intervals de população e gerações
  - Taxas de mutação e crossover
  - Profundidade máxima da árvore de decisão usada na avaliação

Este arquivo deve ser adaptado conforme o experimento.

## Execução do Código
Após configurar: mpi_hosts, /etc/hosts e SSH sem senha

Execute:

```bash
mpirun --hostfile mpi_hosts -np [NUM_PROCESSOS] python main.py teste.txt
```

Exemplo com 5 slots:
```bash
mpirun --hostfile mpi_hosts -np 5 python main.py teste.txt
```

## Observações Importantes
A correta configuração dos arquivos mpi_hosts, teste.txt e /etc/hosts é fundamental.
O SSH sem senha deve funcionar perfeitamente antes de usar o MPI.
Caso algum nó esteja inacessível, o mpirun falhará ao iniciar a execução.
Todos os nós devem ter Python + dependências instalados.

## 📄 Licença
Este repositório é disponibilizado sob os termos de utilização do laboratório LICAP.
Isso significa que você tem permissão para usar, copiar, modificar, mesclar, publicar, distribuir e vender o software, desde que mantenha o aviso de copyright original e uma cópia da licença em qualquer redistribuição.
