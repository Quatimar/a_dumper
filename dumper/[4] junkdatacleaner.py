import os

# Caminho do diretório do script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Pasta 'auletetxt' no diretório pai do script
TARGET_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "auletetxt")

if not os.path.exists(TARGET_DIR):
    print(f"Pasta '{TARGET_DIR}' não encontrada. Verifique se ela existe.")
    input("Pressione Enter para encerrar...")
    exit(1)

deleted_files = []

for root, _, files in os.walk(TARGET_DIR):
    for filename in files:
        if not filename.lower().endswith(".txt"):
            continue

        file_path = os.path.join(root, filename)
        delete = False

        # Verifica tamanho do arquivo
        if os.path.getsize(file_path) == 0:
            delete = True
        else:
            # Verifica conteúdo do arquivo
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read().strip()
                if content == "" or "Não foi encontrado o verbete" in content:
                    delete = True
            except Exception as e:
                print(f"[ERRO] ao ler {file_path}: {e}")
                continue

        if delete:
            try:
                os.remove(file_path)
                deleted_files.append(file_path)
                print(f"[APAGADO] {file_path}")
            except Exception as e:
                print(f"[ERRO] ao apagar {file_path}: {e}")

print(f"\nTotal de arquivos apagados: {len(deleted_files)}")
input("\nPressione Enter para encerrar...")
