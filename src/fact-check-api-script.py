from datetime import datetime
import requests
import os

# --- 1. Parâmetros e configuração ---

# Palavra-chave a ser pesquisada
query = "vacina"

# Código do idioma (português Brasil)
language_code = "pt-BR"

# Tamanho da página (máx. 100)
page_size = 10

# Chave da API (use variável de ambiente por segurança)
API_KEY = os.getenv("FACT_CHECK_API_KEY", "SUA_CHAVE_AQUI")

# URL base da API
base_url = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

# Parâmetros da requisição
params = {
    "query": query,
    "languageCode": language_code,
    "pageSize": page_size,
    "key": API_KEY
}

# --- 2. Função para extrair e imprimir os dados ---

def buscar_claims():
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        dados = response.json()
        claims = dados.get("claims", [])
        print(f"\n✅ {len(claims)} resultados encontrados para '{query}'\n")

        for i, claim in enumerate(claims, 1):
            texto = claim.get("text", "sem texto")
            autor = claim.get("claimant", "autor desconhecido")
            data_afirmacao = claim.get("claimDate", "sem data")
            checagem = claim.get("claimReview", [{}])[0]

            agencia = checagem.get("publisher", {}).get("name", "desconhecida")
            titulo = checagem.get("title", "sem título")
            link = checagem.get("url", "sem link")
            classificacao = checagem.get("textualRating", "sem classificação")

            print(f"🧾 Resultado {i}")
            print(f"🔹 Afirmação: {texto}")
            print(f"👤 Autor: {autor}")
            print(f"📅 Data: {data_afirmacao}")
            print(f"🏷️ Classificação: {classificacao}")
            print(f"🏢 Agência: {agencia}")
            print(f"📖 Título: {titulo}")
            print(f"🔗 Link: {link}\n")

        # Gera log da busca
        with open("log_coleta.txt", "a", encoding="utf-8") as log:
            log.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Busca por '{query}' retornou {len(claims)} resultados.\n")

    else:
        print("❌ Erro na requisição:", response.status_code)
        print(response.text)

# --- 3. Execução ---

if __name__ == "__main__":
    coleta = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n📆 Coleta realizada em: {coleta}")
    buscar_claims()
