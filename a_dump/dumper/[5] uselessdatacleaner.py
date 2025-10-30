import os
import shutil

# Caminho da pasta html (no mesmo diretório do script)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PASTA_HTML = os.path.join(BASE_DIR, "html")

# Confirmação do usuário
print("Apagar arquivos html para liberar espaço?")
resposta = input("Deseja continuar? [Y/N]: ").strip().lower()

if resposta != 'y':
    print("Operação cancelada pelo usuário.")
else:
    if os.path.exists(PASTA_HTML):
        try:
            # Remove todo o conteúdo da pasta, incluindo subpastas
            for root, dirs, files in os.walk(PASTA_HTML, topdown=False):
                for name in files:
                    caminho_file = os.path.join(root, name)
                    os.remove(caminho_file)
                for name in dirs:
                    caminho_dir = os.path.join(root, name)
                    shutil.rmtree(caminho_dir)
            print("Todos os arquivos e subpastas dentro de 'html' foram apagados.")
        except Exception as e:
            print(f"[ERRO] Não foi possível apagar: {e}")
    else:
        print("Pasta 'html' não encontrada.")
