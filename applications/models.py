from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from ckeditor.fields import RichTextField
from django.utils import timezone
from users.models import Deficiencia, TipoDeVaga
import uuid

from projects.models import Project

phone_validator = RegexValidator(regex=r'^\+?1?\d{9,15}$', message='Telefone inválido.')

class GrauFormacao(models.TextChoices):
    GRADUACAO = 'graduacao', 'Graduação (Bacharelado ou Licenciatura)'
    LICENCIATURA = 'licenciatura', 'Licenciatura (específica)'
    BACHARELADO = 'bacharelado', 'Bacharelado (específico)'
    TECNOLOGO = 'tecnologo', 'Tecnólogo'
    ESPECIALIZACAO = 'especializacao', 'Especialização'
    MESTRADO = 'mestrado', 'Mestrado'
    DOUTORADO = 'doutorado', 'Doutorado'
    POS_DOUTORADO = 'pos_doutorado', 'Pós-doutorado'
    OUTRO = 'outro', 'Outro'

class Application(models.Model):
    STATUS_ESCOLHAS = [
        ('rascunho', 'Rascunho'),
        ('pendente', 'Pendente'),
        ('avaliacao', 'Em Avaliação'),
        ('deferida', 'Deferida'),
        ('indeferida', 'Indeferida'),
    ]

    aprovado = models.BooleanField(
        default=False,
        verbose_name="Aprovada para participação",
        help_text="Indica se a candidata foi aprovada no processo seletivo"
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Usuária")
    projeto = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="Projeto")
    criado_em = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    atualizado_em = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    status = models.CharField(max_length=10, choices=STATUS_ESCOLHAS, default='rascunho', verbose_name="Status")
    
    # Identificação e Contato
    como_soube_programa = models.TextField(blank=True, verbose_name="Como soube do programa?")
    telefone_responsavel = models.CharField(max_length=15, blank=True, validators=[phone_validator], verbose_name="Telefone da responsável")
    observacoes = models.TextField(blank=True, verbose_name="Observações")
    curriculo_lattes_url = models.URLField(blank=True, verbose_name="Currículo Lattes (URL)")
    area_atuacao = models.CharField(max_length=100, blank=True, verbose_name="Área de atuação")

    # Vaga e Acessibilidade
    necessita_material_especial = models.BooleanField(default=False, verbose_name="Necessita material especial?")
    tipo_material_necessario = models.TextField(blank=True, verbose_name="Tipo de material necessário")
    laudo_medico_deficiencia = models.BinaryField(null=True, blank=True, verbose_name="Laudo médico de deficiência")
    concorrer_reserva_vagas = models.BooleanField(default=False, verbose_name="Concorrer às vagas reservadas?")
    autodeclaracao_racial = models.BinaryField(null=True, blank=True, verbose_name="Autodeclaração racial")
       
    tipo_deficiencia = models.ForeignKey(
        Deficiencia,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tipo de deficiência"
    )
    
    tipo_de_vaga = models.ForeignKey(
        TipoDeVaga,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Tipo de Vaga"
    )

    # Documentação
    boletim_escolar = models.BinaryField(null=True, blank=True, verbose_name="Boletim escolar")
    termo_autorizacao = models.BinaryField(null=True, blank=True, verbose_name="Termo de autorização")
    rg_frente = models.BinaryField(null=True, blank=True, verbose_name="RG (frente)")
    rg_verso = models.BinaryField(null=True, blank=True, verbose_name="RG (verso)")
    cpf_anexo = models.BinaryField(null=True, blank=True, verbose_name="CPF")
    declaracao_vinculo = models.BinaryField(null=True, blank=True, verbose_name="Declaração de vínculo")
    declaracao_inclusao = models.BinaryField(null=True, blank=True, verbose_name="Declaração de ciência do participante (PPI/PCD/Trans)")
    documentacao_comprobatoria_lattes = models.BinaryField(null=True, blank=True, verbose_name="Documentação Lattes")
    
    # Documentações para o drive
    drive_boletim_escolar = models.CharField(max_length=255, null=True, blank=True, verbose_name="ID do boletim escolar no Drive")
    drive_termo_autorizacao = models.CharField(max_length=255, null=True, blank=True, verbose_name="ID do termo de autorização no Drive")
    drive_rg_frente = models.CharField(max_length=255, null=True, blank=True, verbose_name="ID do RG (frente) no Drive")
    drive_rg_verso = models.CharField(max_length=255, null=True, blank=True, verbose_name="ID do RG (verso) no Drive")
    drive_cpf_anexo = models.CharField(max_length=255, null=True, blank=True, verbose_name="ID do CPF no Drive")
    drive_declaracao_vinculo = models.CharField(max_length=255, null=True, blank=True, verbose_name="ID da declaração de vínculo no Drive")
    drive_documentacao_comprobatoria_lattes = models.CharField(max_length=255, null=True, blank=True, verbose_name="ID da documentação Lattes no Drive")

    # Trajetória Acadêmica e Científica
    grau_formacao = models.CharField(max_length=20,choices=GrauFormacao.choices,verbose_name="Grau de formação mais alto",null=True,blank=True,help_text="Informe o grau de formação mais alto concluído")
    perfil_academico = models.CharField(max_length=150, blank=True, null=True, verbose_name="Perfil acadêmico")
    docencia_superior = models.PositiveIntegerField(blank=True, null=True, verbose_name="Docência no ensino superior")
    docencia_medio = models.PositiveIntegerField(blank=True, null=True, verbose_name="Docência no ensino médio")
    orientacao_ic = models.PositiveIntegerField(blank=True, null=True, verbose_name="Orientação de IC")
    feira_ciencias = models.BooleanField(default=False, verbose_name="Participou de feira de ciências?")
    livro_publicado = models.BooleanField(default=False, verbose_name="Livro publicado?")
    capitulo_publicado = models.BooleanField(default=False, verbose_name="Capítulo publicado?")
    periodico_indexado = models.BooleanField(default=False, verbose_name="Periódico indexado?")
    anais_congresso = models.BooleanField(default=False, verbose_name="Anais de congresso?")
    curso_extensao = models.BooleanField(default=False, verbose_name="Curso de extensão?")
    curso_capacitacao = models.BooleanField(default=False, verbose_name="Curso de capacitação?")
    orientacoes_estudantes = models.BooleanField(default=False, verbose_name="Orientações de estudantes?")
    participacoes_bancas = models.BooleanField(default=False, verbose_name="Participações em bancas?")
    apresentacao_oral = models.BooleanField(default=False, verbose_name="Apresentações orais?")
    premiacoes = models.BooleanField(default=False, verbose_name="Premiações?")
    missao_cientifica = models.BooleanField(default=False, verbose_name="Missão científica?")
    titulo_projeto_submetido = models.CharField(max_length=255, blank=True, null=True,verbose_name="Título do projeto submetido")
    link_projeto = models.URLField(blank=True, null=True, verbose_name="Link para o projeto")
    numero_edicoes_participadas = models.PositiveIntegerField(default=0, verbose_name="Número de edições anteriores do programa")

    # Declarações Finais
    aceite_declaracao_veracidade = models.BooleanField(default=False, verbose_name="Aceite da declaração de veracidade")
    aceite_requisitos_tecnicos = models.BooleanField(default=False, verbose_name="Aceite dos requisitos técnicos")

    # Notas
    portugues = models.DecimalField("Nota em Português", max_digits=4, decimal_places=2, null=True, blank=True)
    matematica = models.DecimalField("Nota em Matemática", max_digits=4, decimal_places=2, null=True, blank=True)
    biologia = models.DecimalField("Nota em Biologia", max_digits=4, decimal_places=2, null=True, blank=True)
    quimica = models.DecimalField("Nota em Química", max_digits=4, decimal_places=2, null=True, blank=True)
    fisica = models.DecimalField("Nota em Física", max_digits=4, decimal_places=2, null=True, blank=True)
    historia = models.DecimalField("Nota em História", max_digits=4, decimal_places=2, null=True, blank=True)
    geografia = models.DecimalField("Nota em Geografia", max_digits=4, decimal_places=2, null=True, blank=True)

    # Avaliação
    ranking = models.FloatField(null=True, blank=True, verbose_name="Pontuação total (ranking)")
    perfil_academico_pontuacao = models.FloatField(default=0.0, verbose_name="Pontuação - Perfil Acadêmico")
    atividade_docente_pontuacao = models.FloatField(default=0.0, verbose_name="Pontuação - Atividade Docente")
    atividade_pesquisa_pontuacao = models.FloatField(default=0.0, verbose_name="Pontuação - Atividade de Pesquisa")
    outras_atividades_pontuacao = models.FloatField(default=0.0, verbose_name="Pontuação - Outras Atividades")


    def clean(self):
        now = timezone.now().date()  
        projeto = getattr(self, 'projeto', None)
        # if not projeto:
        #     raise ValidationError({'projeto': 'O projeto deve ser selecionado.'})
    
        # if not (self.projeto.inicio_inscricoes <= now <= self.projeto.fim_inscricoes):
        #     raise ValidationError("Inscrição fora do prazo permitido do projeto.")

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

class Comentario(models.Model):
    comentario = RichTextField(verbose_name="Comentário")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    aplicacao = models.ForeignKey(Application, on_delete=models.CASCADE)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comentario

