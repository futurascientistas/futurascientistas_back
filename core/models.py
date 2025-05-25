from django.db import models

class Regiao(models.Model):
    nome = models.CharField(max_length=100)
    abreviacao = models.CharField(max_length=3)
    descricao = models.CharField(max_length=100)

    class Meta:
        unique_together = ('nome', 'descricao')

    def __str__(self):
        return self.nome


class Estado(models.Model):
    uf = models.CharField(max_length=2)  # Ex: 'SP'
    nome = models.CharField(max_length=100)  # Ex: 'São Paulo'
    regiao = models.ForeignKey(Regiao, on_delete=models.CASCADE, related_name='estados')

    def __str__(self):
        return self.nome


class Cidade(models.Model):
    nome = models.CharField(max_length=100)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, related_name='cidades')

    def __str__(self):
        return f"{self.nome} - {self.estado.uf}"


class Instituicao(models.Model):
    nome = models.CharField(max_length=200)
    telefone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(unique=True)
    cidade = models.ForeignKey(Cidade, on_delete=models.SET_NULL, null=True, related_name='instituicoes')
    bairro = models.CharField(max_length=100)
    rua = models.CharField(max_length=200)
    numero = models.CharField(max_length=10)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    cep = models.CharField(max_length=9)

    def __str__(self):
        return self.nome
