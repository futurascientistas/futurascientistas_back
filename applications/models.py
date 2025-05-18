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
