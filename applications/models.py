from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid

from projects.models import Project

phone_validator = RegexValidator(regex=r'^\+?1?\d{9,15}$', message='Telefone inválido.')


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
    atualizado_em = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_ESCOLHAS, default='rascunho')
   
    # Identificação e Contato
    como_soube_programa = models.TextField(blank=True)
    telefone_responsavel = models.CharField(max_length=15, blank=True, validators=[phone_validator])
    observacoes = models.TextField(blank=True)
    curriculo_lattes_url = models.URLField(blank=True)

    # Vaga e Acessibilidade
    cota_desejada = models.CharField(max_length=100, blank=True)
    tipo_deficiencia = models.CharField(max_length=200, blank=True)
    necessita_material_especial = models.BooleanField(default=False)
    tipo_material_necessario = models.TextField(blank=True)
    laudo_medico_deficiencia = models.BinaryField(null=True, blank=True)
    concorrer_reserva_vagas = models.BooleanField(default=False)
    autodeclaracao_racial = models.BinaryField(null=True, blank=True)
    mulher_trans = models.BooleanField(default=False)

    # Documentação
    boletim_escolar = models.BinaryField(null=True, blank=True)
    termo_autorizacao = models.BinaryField(null=True, blank=True)
    rg_frente = models.BinaryField(null=True, blank=True)
    rg_verso = models.BinaryField(null=True, blank=True)
    cpf_anexo = models.BinaryField(null=True, blank=True)
    declaracao_vinculo = models.BinaryField(null=True, blank=True)
    documentacao_comprobatoria_lattes = models.BinaryField(null=True, blank=True)

    # Trajetória Acadêmica e Científica
    perfil_academico = models.CharField(max_length=150, blank=True)
    docencia_superior = models.CharField(max_length=150, blank=True)
    docencia_medio = models.CharField(max_length=150, blank=True)
    orientacao_ic = models.CharField(max_length=150, blank=True)
    feira_ciencias = models.BooleanField(default=False)
    livro_publicado = models.BooleanField(default=False)
    capitulo_publicado = models.BooleanField(default=False)
    periodico_indexado = models.BooleanField(default=False)
    anais_congresso = models.BooleanField(default=False)
    curso_extensao = models.BooleanField(default=False)
    curso_capacitacao = models.BooleanField(default=False)
    orientacoes_estudantes = models.BooleanField(default=False)
    participacoes_bancas = models.BooleanField(default=False)
    apresentacao_oral = models.BooleanField(default=False)
    premiacoes = models.BooleanField(default=False)
    missao_cientifica = models.BooleanField(default=False)

    # Declarações Finais
    aceite_declaracao_veracidade = models.BooleanField(default=False)
    aceite_requisitos_tecnicos = models.BooleanField(default=False)

    portugues = models.DecimalField("Nota em Português", max_digits=4, decimal_places=2, null=True, blank=True)
    matematica = models.DecimalField("Nota em Matemática", max_digits=4, decimal_places=2, null=True, blank=True)
    biologia = models.DecimalField("Nota em Biologia", max_digits=4, decimal_places=2, null=True, blank=True)
    quimica = models.DecimalField("Nota em Química", max_digits=4, decimal_places=2, null=True, blank=True)
    fisica = models.DecimalField("Nota em Física", max_digits=4, decimal_places=2, null=True, blank=True)
    historia = models.DecimalField("Nota em História", max_digits=4, decimal_places=2, null=True, blank=True)
    geografia = models.DecimalField("Nota em Geografia", max_digits=4, decimal_places=2, null=True, blank=True)


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

class AcompanhamentoProjeto(models.Model):
    STATUS_PROJETO_CHOICES = [
        ('em_andamento', 'Em Andamento'),
        ('concluido', 'Concluído'),
        ('incompleto', 'Incompleto'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='acompanhamentos')
    projeto = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    data_inicio = models.DateField(auto_now_add=True)
    frequencia = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    nota_final = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status_projeto = models.CharField(max_length=20, choices=STATUS_PROJETO_CHOICES, default='em_andamento')
    projeto_entregue = models.BooleanField(default=False)
    observacoes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('participante', 'projeto')
        verbose_name_plural = 'Acompanhamentos de Projeto'
    
    def __str__(self):
        return f"{self.participante} - {self.projeto}"

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
