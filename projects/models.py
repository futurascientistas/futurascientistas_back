from django.db import models
from users.models import User
from core.models import Regiao, Estado, Cidade
import uuid

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

class ProjectStatusLog(models.Model):
    projeto = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='logs_status')
    status_anterior = models.CharField(max_length=30, null=True, blank=True)
    status_novo = models.CharField(max_length=30)
    status_anterior_display = models.CharField(max_length=30, null=True, blank=True)
    status_novo_display = models.CharField(max_length=30)
    modificado_por = models.CharField(max_length=255, null=True, blank=True, verbose_name='Modificado por (nome e e-mail)')
    data_modificacao = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        get_display = lambda code: dict(STATUS_PROJETO).get(code, code or '')
        self.status_anterior_display = get_display(self.status_anterior)
        self.status_novo_display = get_display(self.status_novo)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.projeto.nome} | {self.status_anterior_display} → {self.status_novo_display} por {self.modificado_por or 'Desconhecido'} em {self.data_modificacao:%d/%m/%Y %H:%M}"

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

    regioes_aceitas = models.ManyToManyField(
        Regiao,
        blank=True,
        related_name='projetos',
        verbose_name='Regiões aceitas'
    )

    estados_aceitos = models.ManyToManyField(
        Estado,
        blank=True,
        related_name='projetos',
        verbose_name='Estados aceitos'
    )

    cidades_aceitas = models.ManyToManyField(
        Cidade,
        blank=True,
        related_name='projetos',
        verbose_name='Cidades aceitas'
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

    data_divulgacao_resultado = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data de divulgação do resultado'
    )

    data_inicio_projeto = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data prevista de início do projeto'
    )

    data_ifm = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data do IFM (Início da Formação de Monitoras)'
    )


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