class ParamsExtracter:
    
    def extract_param_values(self, param_list):
        """
        Extrai os valores min, max e ite de uma lista de parâmetros,
        removendo espaços em branco nas bordas.

        Args:
            param_list (list): Lista com pelo menos 4 elementos, onde os índices 1, 2 e 3
                            contêm os valores relevantes.

        Returns:
            tuple: (min_value, max_value, ite_value) todos como strings com espaços removidos.
        """
        if len(param_list) < 4:
            raise ValueError("A lista deve conter pelo menos 4 elementos.")
        
        return (
            param_list[1].strip(),
            param_list[2].strip(),
            param_list[3].strip()
        )
        
    def parse_line(self, line, skip_first=False):
        """
        Remove o caractere de nova linha, divide por espaço e, se necessário, remove o primeiro elemento.
        """
        parts = line.strip().split()
        return parts[1:] if skip_first else parts
    
    def extrair_valor(self, linha, tipo):
        return tipo(linha.split(":")[1].strip())
    
    def parse_backup_file(self, caminho):
        """
        Lê um arquivo de backup e extrai os valores esperados com segurança.
        
        Retorna:
            dict com as chaves: seed, pop, gen, cross, mut, contador
        """
        conteudo = self.Arquivo.le_arquivo_txt(caminho).splitlines()
        if len(conteudo) < 6:
            raise ValueError("Arquivo de backup incompleto.")
        
        return {
        "seed": self.extrair_valor(conteudo[0], str),
        "pop": self.extrair_valor(conteudo[1], int),
        "gen": self.extrair_valor(conteudo[2], int),
        "cross": self.extrair_valor(conteudo[3], float),
        "mut": self.extrair_valor(conteudo[4], float),
        "contador": self.extrair_valor(conteudo[5], int),
        }


