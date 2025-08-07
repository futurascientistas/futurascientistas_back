import requests

BASE_URL = 'http://localhost:8000'
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU0NjEwOTM2LCJpYXQiOjE3NTQ2MDM3MzYsImp0aSI6ImI1NzdhNDAyOTA0ZDRkNGE4NzllMTkzNGY5NDFiZjk4IiwidXNlcl9pZCI6ImE2ODAzZmE4LWFkM2ItNGNiYi1hNTg3LTBkM2YxMDk3OGQ1NiJ9.no-VxuUIskEKP3_fJWrxAdv1WPYQYaGD5WqC15SYhYM'

HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json',
}

# --- POPULAR COTAS ---
print("\n📥 Populando cotas...")

cotas = [
    "PPI (pretas, pardas, indígenas e quilombolas)",
    "Trans e Travestis",
    "PcD (pessoas com deficiência)"
]

for cota in cotas:
    payload = {
        "nome": cota
    }
    response = requests.post(f"{BASE_URL}/api/cotas/", json=payload, headers=HEADERS)
    
    if response.status_code in (200, 201):
        print(f"✔ Cota '{cota}' criada com sucesso.")
    elif response.status_code == 400 and "unique" in response.text.lower():
        print(f"ℹ Cota '{cota}' já existe.")
    else:
        print(f"❌ Erro ao criar cota '{cota}': {response.status_code} - {response.text}")
