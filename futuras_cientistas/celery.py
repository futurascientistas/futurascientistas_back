import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'futuras_cientistas.settings')

app = Celery('futuras_cientistas')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
