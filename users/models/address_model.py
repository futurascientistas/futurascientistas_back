import uuid
from django.db import models
from core.models import Cidade, Estado
from utils.utils import cep_validator

# Modelo Endereço

class Endereco(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    cep = models.CharField(
        max_length=10, 
        validators=[cep_validator], 
        verbose_name="CEP")
    rua = models.CharField(max_length=150, verbose_name="Rua")
    bairro = models.CharField(max_length=100, verbose_name="Bairro")
    numero = models.CharField(max_length=10, verbose_name="Número")
    complemento = models.CharField(max_length=100, blank=True, verbose_name="Complemento")
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, verbose_name="Cidade")
    estado = models.ForeignKey(Estado, on_delete=models.SET_NULL, null=True, verbose_name="Estado")

    def __str__(self):
        return f"{self.rua}, {self.numero} - {self.bairro}, {self.cidade} - {self.estado}"