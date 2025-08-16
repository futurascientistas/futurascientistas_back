from django.db import models

class Genero(models.Model):
    nome = models.CharField(max_length=100)
    def __str__(self): return self.nome

class Raca(models.Model):
    nome = models.CharField(max_length=100)
    def __str__(self): return self.nome

class Deficiencia(models.Model):
    nome = models.CharField(max_length=100)
    def __str__(self): return self.nome

class TipoDeVaga(models.Model):
    nome = models.CharField(
        max_length=100, 
        unique=True, 
        db_index=True, 
        verbose_name="Nome")
    
    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Tipo de Vaga"
        verbose_name_plural = "Tipos de Vaga"
        ordering = ['nome']
