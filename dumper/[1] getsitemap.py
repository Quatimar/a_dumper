import os
import re
import requests
from tqdm import tqdm
from string import ascii_lowercase

URL = "https://www.aulete.com.br/sitemap.xml"

# Caminhos automáticos
SCRIPT_PATH = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(SCRIPT_PATH)

# Pasta de saída fixa
PASTA_SCRIPT = os.path.join(BASE_DIR, "sitemap")
os.makedirs(PASTA_SCRIPT, exist_ok=True)

# Arquivo principal (todas as URLs)
ARQUIVO_SAIDA = os.path.join(PASTA_SCRIPT, "alllinks.txt")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0 Safari/537.36"
}

print("Baixando sitemap...")

try:
    # Download com barra de progresso
    with requests.get(URL, headers=headers, stream=True, timeout=30) as resp:
        resp.raise_for_status()
        total = int(resp.headers.get('content-length', 0))
        chunks = []
        with tqdm(total=total, unit='B', unit_scale=True, desc="Progresso") as pbar:
            for data in resp.iter_content(chunk_size=8192):
                chunks.append(data)
                pbar.update(len(data))
        conteudo = b''.join(chunks).decode('utf-8', errors='replace')

    # Remove cabeçalho XML e tags
    conteudo = re.sub(
        r'<\?xml[^>]+\?>\s*<urlset[^>]*>', '', conteudo,
        flags=re.DOTALL | re.IGNORECASE
    )
    conteudo = re.sub(r'</?url>', '', conteudo, flags=re.IGNORECASE)
    conteudo = re.sub(r'</?loc>', '', conteudo, flags=re.IGNORECASE)
    conteudo = re.sub(r'</urlset>', '', conteudo, flags=re.IGNORECASE)

    # Limpa linhas vazias e mantém URLs completas
    linhas = [l.strip() for l in conteudo.splitlines() if l.strip()]

    # Cria dicionário de listas por letra inicial (ignorando o prefixo para ordenação)
    subdivisoes = {letra: [] for letra in ascii_lowercase}
    subdivisoes["outros"] = []

    for l in linhas:
        # Remove prefixo só para análise
        sem_prefixo = re.sub(r'^https?://(?:www\.)?aulete\.com\.br/', '', l)
        primeira = sem_prefixo[0].lower() if sem_prefixo else ""
        if primeira in ascii_lowercase:
            subdivisoes[primeira].append(l)
        else:
            subdivisoes["outros"].append(l)

    # Gera arquivos por subdivisão
    total_geral = 0
    for letra in list(ascii_lowercase) + ["outros"]:
        conteudo_letra = subdivisoes[letra]
        if not conteudo_letra:
            continue
        arquivo_letra = os.path.join(PASTA_SCRIPT, f"{letra}.txt")
        with open(arquivo_letra, "w", encoding="utf-8") as f:
            f.write("\n".join(conteudo_letra))
        print(f"{arquivo_letra} salvo com {len(conteudo_letra)} URLs.")
        total_geral += len(conteudo_letra)

    # Também salva o arquivo completo
    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))

    print("\nSitemap processado com sucesso.")
    print(f"Pasta de saída: {PASTA_SCRIPT}")
    print(f"Total de URLs gravadas: {total_geral}")

except Exception as e:
    print(f"Erro ao baixar ou processar: {e}")
