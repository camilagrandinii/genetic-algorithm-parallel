import os

class Diretorio :
    def __init__(self, caminho) :
        self.caminho = caminho
        self.novo_caminho = None

    def create_folder(self, nome_diretorio):
        path = os.path.join(self.caminho, nome_diretorio)
        self.novo_caminho = path
        os.makedirs(path,exist_ok=True)

    def create_folder_in_folder(self, nome_novo_diretorio):
        path = os.path.join(self.novo_caminho, nome_novo_diretorio)
        self.caminho_modelo = path
        os.makedirs(path, exist_ok=True)

    def constroi_caminho(self, nome_diretorio, nome_arquivo):
        path = os.path.join(nome_diretorio, nome_arquivo)
        return path

    def remove_arquivos(self, path):
        for arquivo in os.listdir(path):
            caminho_arquivo = os.path.join(path, arquivo)
            if os.path.isfile(caminho_arquivo):
                os.remove(caminho_arquivo)
        

    def get_path(self):
        return self.caminho_modelo