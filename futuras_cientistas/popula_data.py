import requests
import time

BASE_URL = 'http://127.0.0.1:8000/'
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUxNDE2NzM5LCJpYXQiOjE3NTE0MDk1MzksImp0aSI6IjIzOWUzZWZmNDM0ODQxZjk4YTcyNDgyMzZhZTdmZmFkIiwidXNlcl9pZCI6ImZhNjc2Yzc2LTEzZTQtNGMyZi05ZjFmLWI2NjM5MjUwYjI0ZiJ9.K-87FwaN9OehoUksSD4Qrns3U2KI_UB-GGygMp36rng'
HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json',
}

# --- 1. REGIÕES ---
print("Obtendo dados de estados do IBGE...")
ibge_estados = requests.get('https://servicodados.ibge.gov.br/api/v1/localidades/estados').json()





def criar_itens(lista, endpoint, nome_classe):
    print(f"\n📥 Populando {nome_classe}s...")

    for item in lista:
        if not item:
            print(f"⚠ Nome inválido para {nome_classe}. Ignorado.")
            continue

        payload = {"nome": item}

        try:
            response = requests.post(f"{BASE_URL}/api/{endpoint}/", json=payload, headers=HEADERS)

            if response.status_code in (200, 201):
                print(f"✔ {nome_classe} '{item}' criado.")
            elif response.status_code == 400 and "unique" in response.text.lower():
                print(f"ℹ {nome_classe} '{item}' já existe.")
            else:
                print(f"❌ Erro ao criar {nome_classe} '{item}': {response.status_code} - {response.text}")

        except Exception as e:
            print(f"🚫 Falha ao processar '{item}': {str(e)}")
racas = [
    "Branca",
    "Preta",
    "Parda",
    "Amarela",
    "Indígena"
]
deficiencias = [
    "Deficiência física",
    "Deficiência auditiva",
    "Deficiência visual",
    "Deficiência intelectual",
    "Deficiência múltipla",
    "Transtorno do espectro autista (TEA)"
]
criar_itens(racas, "racas", "Raça")
criar_itens(deficiencias, "deficiencias", "Deficiência")
