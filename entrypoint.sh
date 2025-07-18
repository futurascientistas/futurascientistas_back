#!/bin/bash
set -e

echo ">> Rodando makemigrations"
python manage.py makemigrations

echo ">> Rodando migrate"
python manage.py migrate

echo ">> Criando superusuário (se não existir)"
python manage.py shell < create_superuser.py

echo ">> Iniciando servidor Django"
exec "$@"

