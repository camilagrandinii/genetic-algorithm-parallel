
class MOGATerminalLogger:
    @staticmethod
    def print_generation_results(generation_count: int, population_size: int, record, diretorio, FILE_NAME):
        FILE_NAME = "output_"+FILE_NAME
        nome_arquivo = diretorio.constroi_caminho(diretorio.get_path(), FILE_NAME)
        with open(nome_arquivo, "a") as file:
            log = (
                "Numero da geracao: "
                + generation_count.__str__()
                + "\n"
                + "Tamanho da populacao: "
                + population_size.__str__()
                + "\n"
                + "Total de filhos repetidos: "
                + record["Filhos"]["Ind. Repetidos\t "].__str__()
                + "\n"
                + "(Filhos abaixo da média, Filhos acima da média) = "
                + record["Filhos"]["Piores / Melhores  "].__str__()
                + "\n"
                # + "1) Media  "
                # + record["Fitness"]["1) Media   "][0].__str__()
                # + "\n"
                # + "1) Media  "
                # + record["Fitness"]["1) Media   "][1].__str__()
                # + "\n"
                # + "2) Desvio Padrao "
                # + record["Fitness"]["2) Desvio Padrao   "][0].__str__()
                # + "\n"
                # + "2) Desvio Padrao "
                # + record["Fitness"]["2) Desvio Padrao   "][1].__str__()
                # + "\n"
                # + "3) Minimo "
                # + record["Fitness"]["3) Minimo  "][0].__str__()
                # + "\n"
                # + "3) Minimo "
                # + record["Fitness"]["3) Minimo  "][1].__str__()
                # + "\n"
                # + "4) Maximo "
                # + record["Fitness"]["4) Maximo  "][0].__str__()
                # + "\n"
                # + "4) Maximo "
                # + record["Fitness"]["4) Maximo  "][1].__str__()
                # +"\n"
            )
            file.write(log)
            file.close()
            print(log)
