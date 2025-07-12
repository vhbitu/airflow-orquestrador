from datetime import datetime
import requests
import os
import json

# --- 1. Parâmetros e configuração ---

query = "água"
language_code = "pt-BR"
page_size = 100
API_KEY = os.getenv("FACT_CHECK_API_KEY", "SUA_CHAVE_AQUI")

base_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

# Arquivos para salvar
ARQUIVO_DADOS = "dados_novos.json"
ARQUIVO_HISTORICO = "historico_urls.json"
ARQUIVO_LOG = "log_coleta.txt"

# --- 2. Carregar histórico existente (ou criar vazio) ---
if os.path.exists(ARQUIVO_HISTORICO):
    with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
        historico_urls = set(json.load(f))
else:
    historico_urls = set()

# --- 3. Função de busca com paginação e filtro por duplicatas ---
def buscar_claims():
    pagina = 1
    novas_claims = []
    total_requisicoes = 0
    next_page_token = None

    while True:
        print(f"🔄 Página {pagina}...")

        params = {
            "query": query,
            "languageCode": language_code,
            "pageSize": page_size,
            "key": API_KEY
        }

        if next_page_token:
            params["pageToken"] = next_page_token

        response = requests.get(base_url, params=params)
        total_requisicoes += 1

        if response.status_code != 200:
            print("❌ Erro:", response.status_code)
            print(response.text)
            break

        dados = response.json()
        claims = dados.get("claims", [])
        next_page_token = dados.get("nextPageToken")

        novos_encontrados = 0

        for claim in claims:
            checagem = claim.get("claimReview", [{}])[0]
            url = checagem.get("url", "")

            if url and url not in historico_urls:
                novas_claims.append(claim)
                historico_urls.add(url)
                novos_encontrados += 1

        print(f"✅ {novos_encontrados} novos resultados na página {pagina}")

        if not next_page_token:
            break

        pagina += 1

    # Salvar os novos dados (se houver)
    if novas_claims:
        with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
            json.dump(novas_claims, f, ensure_ascii=False, indent=4)

        with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
            json.dump(list(historico_urls), f, ensure_ascii=False, indent=2)

        with open(ARQUIVO_LOG, "a", encoding="utf-8") as log:
            log.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {len(novas_claims)} novos registros adicionados para '{query}'\n")

        print(f"\n📝 {len(novas_claims)} novas checagens salvas em '{ARQUIVO_DADOS}'")
    else:
        print("\n📦 Nenhuma nova checagem encontrada.")

# --- 4. Execução ---
if __name__ == "__main__":
    print(f"\n📅 Coleta iniciada em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    buscar_claims()

