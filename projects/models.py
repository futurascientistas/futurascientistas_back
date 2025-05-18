from django.db import models
from users.models import User
from django.contrib.postgres.fields import ArrayField
import uuid

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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=255, verbose_name='Nome')
    descricao = models.TextField(verbose_name='Descrição')
    criado_por = models.EmailField(null=True, blank=True, verbose_name='Criado por (e-mail)')
    atualizado_por = models.EmailField(null=True, blank=True, verbose_name='Atualizado por (e-mail)')
    
    tutora = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='projetos_tutorados',
        verbose_name='Tutora'
    )
    eh_remoto = models.BooleanField(default=False, verbose_name='É remoto')
    regioes_aceitas = ArrayField(
        models.CharField(max_length=20, choices=REGIOES_BRASIL),
        default=list,
        verbose_name='Regiões aceitas',
        blank=True
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

    vagas = models.PositiveIntegerField(verbose_name='Vagas')
    ativo = models.BooleanField(default=True, verbose_name='Ativo')
    
    inicio_inscricoes = models.DateTimeField(verbose_name='Início das inscrições')
    fim_inscricoes = models.DateTimeField(verbose_name='Fim das inscrições')

    data_inicio = models.DateTimeField(verbose_name='Data de início')
    data_fim = models.DateTimeField(verbose_name='Data de fim')

    criado_em = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Projeto'
        verbose_name_plural = 'Projetos'

class ImportacaoProjeto(models.Model):
    arquivo = models.FileField(upload_to='importacoes/')
    data_importacao = models.DateTimeField(auto_now_add=True)
    linhas_lidas = models.IntegerField(default=0)
    projetos_criados = models.IntegerField(default=0)
    projetos_ignorados = models.IntegerField(default=0)
    linhas_ignoradas_texto = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Importação em {self.data_importacao.strftime('%d/%m/%Y %H:%M')}"