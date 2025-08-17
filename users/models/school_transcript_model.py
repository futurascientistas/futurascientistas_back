import uuid
from django.db import models
from futuras_cientistas import settings


class HistoricoEscolar(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    historico_escolar = models.FileField("Upload do histórico escolar", null=True, blank=True)
    def __str__(self):
        return f"Histórico de {self.usuario.username}"

class Disciplina(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.nome

class Nota(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    historico = models.ForeignKey(HistoricoEscolar, related_name='notas', on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    bimestre = models.PositiveSmallIntegerField("Bimestre", choices=[(1, '1º'), (2, '2º')])
    valor = models.DecimalField("Valor da Nota", max_digits=4, decimal_places=2, null=True, blank=True)
    
    class Meta:
        unique_together = ('historico', 'disciplina', 'bimestre')

    def __str__(self):
        return f"{self.disciplina.nome} - {self.bimestre}º Bimestre ({self.historico.usuario.username})"
