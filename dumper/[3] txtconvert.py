import os
import re
import time
import chardet
from bs4 import BeautifulSoup

# === CONFIGURAÇÕES ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_BASE = os.path.join(BASE_DIR, "html")            # pasta com os HTMLs (e subpastas alfabéticas)
OUTPUT_BASE = os.path.join(os.path.dirname(BASE_DIR), "auletetxt")  # pasta de saída
processed_files = set()

# === FUNÇÕES ===
def rename_missing_html():
    """Renomeia arquivos sem extensão para .html."""
    print("=== RENOMEANDO ARQUIVOS SEM EXTENSÃO ===")
    renamed = 0
    total = 0
    for root, _, files in os.walk(INPUT_BASE):
        for filename in files:
            total += 1
            name, ext = os.path.splitext(filename)
            if ext == "":
                old_path = os.path.join(root, filename)
                new_path = os.path.join(root, filename + ".html")
                if not os.path.exists(new_path):
                    os.rename(old_path, new_path)
                    renamed += 1
                    print(f"[RENOMEADO] {filename} → {filename}.html")
    print(f"Total de arquivos verificados: {total}")
    print(f"Arquivos renomeados: {renamed}\n")

def detect_encoding(filepath):
    """Detecta a codificação de um arquivo."""
    with open(filepath, "rb") as f:
        raw = f.read()
    result = chardet.detect(raw)
    encoding = result["encoding"] or "utf-8"
    return raw, encoding

def clean_text(text):
    """Remove quebras de linha e espaços múltiplos."""
    text = re.sub(r'\s*\n\s*', ' ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def extract_text_from_html(input_path):
    """Extrai o texto do bloco específico do HTML."""
    raw, encoding = detect_encoding(input_path)
    try:
        html = raw.decode(encoding, errors="replace")
    except Exception:
        html = raw.decode("utf-8", errors="replace")

    soup = BeautifulSoup(html, "html.parser")
    original = soup.find("div", id="definicao_verbete_homologado_original")

    if original:
        text = original.get_text(separator="\n", strip=True)
        text = clean_text(text)
    else:
        text = "[ERRO] Bloco 'definicao_verbete_homologado_original' não encontrado."

    return text, encoding

def process_html_files():
    """Percorre todos os HTMLs e converte para TXT."""
    print("=== CONVERSOR DE VERBETES ===")
    print(f"Entrada: {INPUT_BASE}")
    print(f"Saída:   {OUTPUT_BASE}\n")

    converted = 0
    total = 0
    per_folder_count = {}

    for root, _, files in os.walk(INPUT_BASE):
        rel_path = os.path.relpath(root, INPUT_BASE)
        if rel_path == ".":
            continue  # evita criar uma subpasta "html" dentro do output

        letter = os.path.basename(rel_path).upper() or "OUTROS"
        output_folder = os.path.join(OUTPUT_BASE, letter)
        os.makedirs(output_folder, exist_ok=True)

        html_files = [f for f in files if f.lower().endswith(".html")]
        per_folder_count[letter] = len(html_files)

        for filename in html_files:
            total += 1
            if filename in processed_files:
                continue

            input_path = os.path.join(root, filename)
            output_name = os.path.splitext(filename)[0] + ".txt"
            output_path = os.path.join(output_folder, output_name)

            text, encoding = extract_text_from_html(input_path)

            with open(output_path, "w", encoding="utf-8", errors="ignore") as out:
                out.write(text)

            converted += 1
            processed_files.add(filename)
            print(f"[OK] {letter}/{filename} → {output_name} ({encoding})")

    print("\n=== RESUMO POR PASTA ===")
    for letter, count in sorted(per_folder_count.items()):
        print(f"{letter}: {count} arquivos encontrados")

    print(f"\nConversão concluída!")
    print(f"Arquivos convertidos: {converted}/{total}\n")

# === EXECUÇÃO ===
if __name__ == "__main__":
    rename_missing_html()
    process_html_files()
