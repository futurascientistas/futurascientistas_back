from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid

from projects.models import Project

class Application(models.Model):
    STATUS_ESCOLHAS = [
        ('rascunho', 'Rascunho'),
        ('pendente', 'Pendente'),
        ('avaliacao', 'Em Avaliacao'),
        ('deferida', 'Deferida'),
        ('indeferida', 'indeferida'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    projeto = models.ForeignKey(Project, on_delete=models.CASCADE)
    criado_em = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_ESCOLHAS, default='rascunho')

    def clean(self):
        now = timezone.now()
        if not (self.projeto.inicio_inscricoes <= now <= self.projeto.fim_inscricoes):
            raise ValidationError("Inscrição fora do prazo permitido do projeto.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class ApplicationStatusLog(models.Model):
    inscricao = models.ForeignKey('Application', on_delete=models.CASCADE, related_name='logs_status')
    projeto = models.ForeignKey(Project, on_delete=models.CASCADE)
    status_anterior = models.CharField(max_length=10, null=True, blank=True)
    status_novo = models.CharField(max_length=10)
    status_anterior_display = models.CharField(max_length=50, null=True, blank=True)
    status_novo_display = models.CharField(max_length=50)
    modificado_por = models.CharField(max_length=255, null=True, blank=True, verbose_name='Modificado por (nome e e-mail)')
    data_modificacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        anterior = self.status_anterior_display or self.status_anterior or "-"
        novo = self.status_novo_display or self.status_novo or "-"
        return f"Inscrição {self.inscricao.id} | {anterior} → {novo} por {self.modificado_por or 'Desconhecido'} em {self.data_modificacao:%d/%m/%Y %H:%M}"
