import os
import re
import json
import requests
import chardet
import unicodedata
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# ===== Configurações =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "html")
os.makedirs(OUTPUT_DIR, exist_ok=True)

SITEMAP_DIR = os.path.join(BASE_DIR, "sitemap")
if not os.path.exists(SITEMAP_DIR):
    print(f"Pasta 'sitemap' não encontrada em {BASE_DIR}.")
    exit(1)

REGISTRO_FILE = os.path.join(OUTPUT_DIR, "registro.json")

MAX_WORKERS = 16
TIMEOUT = 15

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0 Safari/537.36"
})

# ===== Utilitários =====
def get_filename_from_url(url):
    name = os.path.basename(urlparse(url).path) or "download"
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    name = re.sub(r'[^a-zA-Z0-9._-]', '_', name)
    return name

def detect_encoding(resp, content_bytes):
    m = re.search(r"charset=([^\s;]+)", resp.headers.get("content-type", ""), flags=re.I)
    if m:
        return m.group(1).strip('"').strip("'")
    snippet = content_bytes[:4096].decode('ascii', errors='ignore')
    m = re.search(r'<meta\s+charset=["\']?([^"\'>\s]+)', snippet, flags=re.I)
    if m:
        return m.group(1)
    m2 = re.search(r'charset=([^"\'>\s]+)', snippet, flags=re.I)
    if m2:
        return m2.group(1)
    if resp.apparent_encoding:
        return resp.apparent_encoding
    res = chardet.detect(content_bytes)
    return res.get('encoding') or 'utf-8'

def is_binary(resp):
    ctype = resp.headers.get("content-type", "").lower()
    return any(x in ctype for x in ('image/', 'audio/', 'video/', 'application/pdf', 'application/octet-stream'))

def limpar_texto(text):
    return re.sub(r'[^\x00-\x7FÀ-ÿ\u00A0-\u00FF\s\w.,;:!?()/\-]', '', text)

def carregar_registro():
    if os.path.exists(REGISTRO_FILE):
        with open(REGISTRO_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def salvar_registro(registro):
    with open(REGISTRO_FILE, 'w', encoding='utf-8') as f:
        json.dump(registro, f, indent=2, ensure_ascii=False)

def limpar_registro():
    if os.path.exists(REGISTRO_FILE):
        os.remove(REGISTRO_FILE)
    print("\nHistórico de downloads apagado com sucesso.\n")

def download_and_save(url, subfolder):
    try:
        resp = session.get(url, timeout=TIMEOUT)
        resp.raise_for_status()

        filename = get_filename_from_url(url)
        path = os.path.join(subfolder, filename)

        if is_binary(resp):
            with open(path, "wb") as f:
                f.write(resp.content)
            return True, f"[BINÁRIO] {filename}"

        enc = detect_encoding(resp, resp.content)
        text = resp.content.decode(enc, errors="replace")

        if 'html' in resp.headers.get("content-type", "").lower():
            try:
                soup = BeautifulSoup(text, "html.parser")
                text = soup.prettify()
            except Exception:
                pass

        text = limpar_texto(text)

        with open(path, "w", encoding="utf-8", errors="replace") as f:
            f.write(text)

        return True, f"[TEXTO] {filename} ({enc})"

    except Exception as e:
        return False, f"[ERRO] {url} -> {e}"

# ===== Menu de seleção =====
def selecionar_letras(arquivos, registro):
    print("\nArquivos disponíveis na pasta 'sitemap':")

    # Ordenar com "alllinks.txt" primeiro, seguido de A-Z e "outros" por último
    tudo = [f for f in arquivos if f.lower() == "alllinks.txt"]
    alfabeto = sorted([f for f in arquivos if f.lower() not in ("alllinks.txt", "outros.txt")])
    outros = [f for f in arquivos if f.lower().startswith("outros")]
    arquivos_ordenados = tudo + alfabeto + outros

    concluidos = [f for f in arquivos_ordenados if registro.get(os.path.splitext(f)[0], {}).get("concluido")]
    nao_concluidos = [f for f in arquivos_ordenados if f not in concluidos]

    def nome_exibicao(f):
        if f.lower() == "alllinks.txt":
            return "Tudo"
        base = os.path.splitext(f)[0]
        return base.upper() if base != "outros" else "Outros"

    print("\nConcluídos:")
    if concluidos:
        print("  " + ", ".join(nome_exibicao(f) for f in concluidos))
    else:
        print("  (nenhum concluído ainda)")

    print("\nPendentes:")
    print("  " + ", ".join(nome_exibicao(f) for f in nao_concluidos))

    print("\nDigite o intervalo de letras (ex: a-f, a,c,e-f, outros, tudo) ou:")
    print("[1] Limpar histórico de downloads")
    print("[2] Sair")
    escolha = input("→ ").lower().replace(" ", "")

    if escolha == "1":
        limpar_registro()
        return selecionar_letras(arquivos, {})
    if escolha == "2":
        print("Encerrando o programa.")
        exit(0)

    selecionados = set()
    ranges = escolha.split(",")
    for r in ranges:
        if r == "outros":
            for f in arquivos_ordenados:
                if f.lower().startswith("outros"):
                    selecionados.add(f)
        elif r == "tudo":
            for f in arquivos_ordenados:
                if f.lower() == "alllinks.txt":
                    selecionados.add(f)
        elif "-" in r:
            inicio, fim = r.split("-")
            for f in arquivos_ordenados:
                base = os.path.splitext(f)[0]
                if base and base[0].lower() >= inicio and base[0].lower() <= fim:
                    selecionados.add(f)
        else:
            for f in arquivos_ordenados:
                if os.path.splitext(f)[0].startswith(r):
                    selecionados.add(f)

    selecionados = sorted(selecionados, key=lambda x: (x.lower() == "outros.txt", x))
    return selecionados

# ===== Processamento =====
def processar_arquivo(arquivo, registro):
    file_path = os.path.join(SITEMAP_DIR, arquivo)
    subfolder_name = os.path.splitext(arquivo)[0]
    subfolder_path = os.path.join(OUTPUT_DIR, subfolder_name)
    os.makedirs(subfolder_path, exist_ok=True)

    with open(file_path, encoding='utf-8') as f:
        urls = [u.strip() for u in f if u.strip()]

    print(f"\nIniciando downloads do arquivo '{arquivo}' ({len(urls)} URLs)...")
    falhas = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(download_and_save, u, subfolder_path): u for u in urls}
        for i, fut in enumerate(as_completed(futures), 1):
            sucesso, res = fut.result()
            print(f"{i:>3}/{len(urls)} - {res}")
            if not sucesso:
                falhas.append(futures[fut])

    registro[subfolder_name] = {
        "concluido": len(falhas) == 0,
        "falhas": falhas
    }
    salvar_registro(registro)
    return falhas

# ===== Loop principal =====
def main():
    while True:
        arquivos = [f for f in os.listdir(SITEMAP_DIR) if f.lower().endswith('.txt')]
        if not arquivos:
            print("Nenhum arquivo .txt encontrado na pasta 'sitemap'.")
            return

        registro = carregar_registro()
        selecionados = selecionar_letras(arquivos, registro)

        for arquivo in selecionados:
            subname = os.path.splitext(arquivo)[0]
            if registro.get(subname, {}).get("concluido", False):
                print(f"\nArquivo '{arquivo}' já concluído, pulando...")
                continue

            falhas = processar_arquivo(arquivo, registro)

            while falhas:
                print(f"\n{len(falhas)} URLs falharam no arquivo '{arquivo}'.")
                print("O que deseja fazer?")
                print("[1] Tentar novamente")
                print("[2] Ignorar e marcar como concluído")
                print("[3] Sair (manter como incompleto)")
                escolha = input("→ ").strip()

                if escolha == "1":
                    print(f"\nRepetindo {len(falhas)} URLs que falharam...")
                    subfolder_path = os.path.join(OUTPUT_DIR, subname)
                    nova_falhas = []
                    for url in falhas:
                        sucesso, res = download_and_save(url, subfolder_path)
                        print(res)
                        if not sucesso:
                            nova_falhas.append(url)
                    falhas = nova_falhas
                    registro[subname]["falhas"] = falhas
                    registro[subname]["concluido"] = len(falhas) == 0
                    salvar_registro(registro)

                elif escolha == "2":
                    registro[subname]["falhas"] = []
                    registro[subname]["concluido"] = True
                    salvar_registro(registro)
                    print(f"Pasta '{subname}' marcada como concluída (falhas ignoradas).")
                    break

                elif escolha == "3":
                    print("Saindo sem marcar como concluído.")
                    salvar_registro(registro)
                    return
                else:
                    print("Opção inválida. Tente novamente.")

        print("\nTodos os downloads selecionados foram processados.")
        opcao = input("\nDeseja baixar outras letras? (S/N): ").strip().lower()
        if opcao != "s":
            print("Encerrando o programa.")
            break

if __name__ == "__main__":
    main()
