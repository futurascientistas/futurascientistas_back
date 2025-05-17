from django.db import models
from users.models import User
from django.contrib.postgres.fields import ArrayField

REGIOES_BRASIL = [
    ('NORTE', 'Norte'),
    ('NORDESTE', 'Nordeste'),
    ('CENTRO-OESTE', 'Centro-Oeste'),
    ('SUDESTE', 'Sudeste'),
    ('SUL', 'Sul'),
]

FORMATOS = [
    ('presencial', 'Presencial'),
    ('remoto', 'Remoto'),
]

STATUS_PROJETO = [
    ('rascunho', 'Rascunho'),
    ('inscricoes_abertas', 'Inscrições Abertas'),
    ('avaliacao_inscricoes', 'Avaliação das Inscrições'),
    ('inscricoes_aprovadas', 'Inscrições Aprovadas'),
    ('em_andamento', 'Em Andamento'),
    ('avaliacao_projeto', 'Avaliação do Projeto'),
    ('finalizado', 'Finalizado'),
]

class Project(models.Model):
    nome = models.CharField(max_length=255, verbose_name='Nome')
    descricao = models.TextField(verbose_name='Descrição')
    criado_por = models.ForeignKey(
        User, 
        related_name='projetos_criados',
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Criado por'
    )
    eh_remoto = models.BooleanField(default=False, verbose_name='É remoto')
    regioes_aceitas = ArrayField(
        models.CharField(max_length=20, choices=REGIOES_BRASIL),
        default=list,
        verbose_name='Regiões aceitas'
    )
    formato = models.CharField(
        max_length=20,
        choices=FORMATOS,
        default='presencial',
        verbose_name='Formato'
    )
    
    status = models.CharField(
        max_length=30,
        choices=STATUS_PROJETO,
        default='rascunho',
        verbose_name='Status'
    )

    data_inicio = models.DateTimeField(verbose_name='Data de início')
    data_fim = models.DateTimeField(verbose_name='Data de fim')
    vagas = models.PositiveIntegerField(verbose_name='Vagas')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    atualizado_por = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name='projetos_atualizados',
        verbose_name='Atualizado por'
    )

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Projeto'
        verbose_name_plural = 'Projetos'
