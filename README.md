
# 🧪 Futura Cientistas - Projeto Django

Projeto desenvolvido com Django e PostgreSQL.

## 🚀 Como configurar e rodar o projeto localmente

### 1. Clone o repositório

```bash
git clone https://github.com/viradacafe/futuras-cientistas.git
cd futuras-cientistas
```

### 2. Crie o arquivo `requirements.txt`

Crie um arquivo chamado `requirements.txt` na raiz do projeto e cole o seguinte conteúdo:

```
asgiref==3.8.1
Django==5.2.1
django-filter==25.1
djangorestframework==3.16.0
djangorestframework-simplejwt==5.5.0
Markdown==3.8
psycopg==3.2.7
psycopg2-binary==2.9.10
PyJWT==2.9.0
python-decouple==3.8
sqlparse==0.5.3
tzdata==2025.2
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados

No arquivo `settings.py`, atualize a configuração do banco com os dados corretos:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nome_do_banco',
        'USER': 'seu_user',
        'PASSWORD': 'sua_senha',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Acesse o diretório da aplicação

```bash
cd futuras_cientistas
```

### 6. Rode o servidor local

```bash
python manage.py runserver
```

---

