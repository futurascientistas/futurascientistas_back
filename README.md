
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
django-cors-headers==4.7.0
django-filter==25.1
djangorestframework==3.16.0
djangorestframework-simplejwt==5.5.0
Markdown==3.8
numpy==2.2.6
openpyxl==3.1.5
pandas==2.3.0
psycopg==3.2.7
PyJWT==2.9.0
python-dateutil==2.9.0.post0
python-decouple==3.8
python-magic==0.4.27
pytz==2025.2
six==1.17.0
sqlparse==0.5.3
tzdata==2025.2
celery==5.3.0
redis==4.5.1
psycopg2-binary==2.9.6
django-celery-beat

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

