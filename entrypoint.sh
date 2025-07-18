#!/bin/bash
set -e

echo ">> Rodando makemigrations"
python manage.py makemigrations

echo ">> Rodando migrate"
python manage.py migrate

echo ">> Iniciando servidor Django"
exec "$@"
