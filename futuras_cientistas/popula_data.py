import requests
import time

BASE_URL = 'http://localhost:8000'
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUwNzEyODQwLCJpYXQiOjE3NTA3MDU2NDAsImp0aSI6IjkxOWI1NDNkNDFkNDQ5ZjY4Zjg4NjQ1OWJlNzdhZTY0IiwidXNlcl9pZCI6ImE3MDg1ZDI3LWExNGItNDZmYi04ZTk0LTMyYWFmMGQ4ZTRmNyJ9.27iVhEPF7mq3YdC-2Vl3XEIUfZNa87AGz_KcMOYNGNg'
HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json',
}

# --- 1. REGIÕES ---
print("Obtendo dados de estados do IBGE...")
ibge_estados = requests.get('https://servicodados.ibge.gov.br/api/v1/localidades/estados').json()

regioes_dict = {}
for estado in ibge_estados:
    regiao_info = estado['regiao']
    regioes_dict[regiao_info['nome']] = {
        'nome': regiao_info['nome'],
        'abreviacao': regiao_info['sigla'],
        'descricao': f"Região {regiao_info['nome']}"
    }

print("\nPopulando regiões...")
for regiao in regioes_dict.values():
    response = requests.post(f'{BASE_URL}/api/regioes/', json=regiao, headers=HEADERS)
    if response.status_code in (200, 201):
        print(f"✔ Região {regiao['nome']} criada")
    else:
        print(f"❌ Erro ao criar região {regiao['nome']}: {response.text}")

# --- 2. ESTADOS ---
print("\nPopulando estados...")
for estado in ibge_estados:
    data = {
        'uf': estado['sigla'],
        'nome': estado['nome'],
        'regiao_nome': estado['regiao']['nome']
    }

    response = requests.post(f'{BASE_URL}/api/estados/', json=data, headers=HEADERS)
    if response.status_code in (200, 201):
        print(f"✔ Estado {estado['nome']} criado")
    else:
        print(f"❌ Erro ao criar estado {estado['nome']}: {response.text}")

# --- 3. CIDADES ---
print("\nPopulando cidades (modo bulk)...")
for estado in ibge_estados:
    sigla = estado['sigla']
    nome = estado['nome']
    municipios_response = requests.get(f'https://servicodados.ibge.gov.br/api/v1/localidades/estados/{sigla}/municipios')

    if municipios_response.status_code != 200:
        print(f"⚠ Erro ao buscar cidades de {sigla}")
        continue

    municipios = municipios_response.json()
    cidades_bulk = []

    for cidade in municipios:
        cidades_bulk.append({
            'nome': cidade['nome'],
            'estado_nome': nome
        })

    res = requests.post(f'{BASE_URL}/api/cidades/criar_varios/', json=cidades_bulk, headers=HEADERS)
    if res.status_code in (200, 201):
        print(f"🟢 {len(cidades_bulk)} cidades criadas para {nome}")
    else:
        print(f"🔴 Erro ao criar cidades de {nome}: {res.text}")

print("\nPopulação concluída!")


# --- 4. GÊNEROS ---
print("\nPopulando gêneros (um por um)...")

generos = [
    "Mulher cisgênero",
    "Mulher transgênero",
    "Homem cisgênero",
    "Homem transgênero",
    "Pessoa não binária",
    "Pessoa agênero",
    "Pessoa intersexo",
    "Prefere não dizer",
    "Outro"
]

for genero in generos:
    payload = {
        "nome": genero
    }
    response = requests.post(f"{BASE_URL}/api/generos/", json=payload, headers=HEADERS)
    
    if response.status_code in (200, 201):
        print(f"✔ Gênero '{genero}' criado com sucesso.")
    elif response.status_code == 400 and "unique" in response.text.lower():
        print(f"ℹ Gênero '{genero}' já existe.")
    else:
        print(f"❌ Erro ao criar gênero '{genero}': {response.status_code} - {response.text}")



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
