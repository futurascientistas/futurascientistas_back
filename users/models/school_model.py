import uuid
from django.db import models
from users.models import Endereco
from utils.utils import phone_validator

# Modelo Tipo de Ensino
class TipoEnsino(models.Model):
    nome = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        verbose_name="Nome")

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Tipo de Ensino"
        verbose_name_plural = "Tipos de Ensino"
        ordering = ['nome']

# Modelo Escola
class Escola(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    nome_escola = models.CharField(
        max_length=150, 
        verbose_name="Nome da escola")
    tipo_ensino = models.ForeignKey(
        TipoEnsino, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Tipo de Ensino")
    endereco = models.ForeignKey(
        Endereco, 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name="Endereço da escola")
    telefone_escola = models.CharField(
        max_length=15, 
        blank=True, 
        validators=[phone_validator], 
        verbose_name="Telefone da escola")
    telefone_responsavel_escola = models.CharField(
        max_length=15, 
        blank=True, 
        validators=[phone_validator], 
        verbose_name="Telefone do responsável da escola")

    def __str__(self):
        return self.nome_escola

