import requests
import time

BASE_URL = 'http://localhost:8000'
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYxMDA2NzE5LCJpYXQiOjE3NjA5OTk1MTksImp0aSI6IjUwYTY1NTI3NzM0NjRmMzI4YTFmYTNjMDVjOGMzYjM4IiwidXNlcl9pZCI6IjE2MmQxN2RhLWUyNzMtNDM4OC1hMGU1LWFlNTBlY2QxODFmMSJ9._eBoJT2F_9xiA9ZqANndiYTzQ820fg0JgxdJJFktx1k'
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

# --- 5. PROJETOS ---

HEADERS_2 = {
    'Authorization': f'Bearer {TOKEN}',
}

file_path = "C:\\Users\\gabri\\Desktop\\virada_master_final\\futurascientistas_back\\importacoes\\Projetos_TESTE.xlsx"


print(file_path)


try:
    # Abre o arquivo em modo de leitura binária
    with open(file_path, 'rb') as f:
        # O objeto `files` é crucial para o envio de arquivos
        files = {'arquivo': f}
        
        # Envia a requisição POST com o objeto `files`
        response = requests.post(
            f"{BASE_URL}/projetos/importar-projetos/",
            headers=HEADERS_2,
            files=files  # Usa o parâmetro `files` para enviar o arquivo
        )

        print(response)

    # Verifica o status da resposta
    if response.status_code == 200:
        print("✔ Projetos importados com sucesso.")
    elif response.status_code == 400:
        print(f"❌ Erro na importação: {response.text}")
    else:
        print(f"❌ Erro ao importar projetos: {response.status_code} - {response.text}")

except requests.exceptions.RequestException as e:
    print(f"❌ Erro na requisição: {e}")