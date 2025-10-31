import os

BASE_DIR = "auletetxt"

# One-time scan
files = [os.path.join(root, f)
         for root, _, fs in os.walk(BASE_DIR)
         for f in fs if f.endswith(".txt")]

while True:
    term = input("\nDigite a palavra para buscar (ou ENTER para sair): ").strip()
    if not term:
        break

    matches = [f for f in files if term.lower() in os.path.basename(f).lower()]

    if not matches:
        print("Nenhum arquivo encontrado.")
        continue

    for i, f in enumerate(matches, 1):
        print(f"[{i}] {os.path.basename(f)}")
    print(f"[{len(matches)+1}] Cancelar busca")

    op = input("Escolha uma opção: ").strip()
    if not op.isdigit() or int(op) > len(matches)+1:
        print("Opção inválida.")
        continue

    op = int(op)
    if op == len(matches)+1:
        continue

    with open(matches[op-1], encoding="utf-8", errors="ignore") as fh:
        print(fh.read())

    input("\nPressione ENTER para continuar...")
