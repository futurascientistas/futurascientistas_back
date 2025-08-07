from django.contrib.auth.models import AbstractUser, BaseUserManager, Group
from django.db import models
from django.core.validators import RegexValidator, FileExtensionValidator
import uuid

from futuras_cientistas import settings
from .managers import UserManager
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

# Validadores
cpf_validator = RegexValidator(regex=r'^\d{11}$', message='CPF deve conter 11 dígitos numéricos.')
phone_validator = RegexValidator(regex=r'^\+?1?\d{9,15}$', message='Telefone inválido.')
extensoes_aceitas = FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])

# Modelos auxiliares
class Genero(models.Model):
    nome = models.CharField(max_length=100)
    def __str__(self): return self.nome

class Raca(models.Model):
    nome = models.CharField(max_length=100)
    def __str__(self): return self.nome

class Deficiencia(models.Model):
    nome = models.CharField(max_length=100)
    def __str__(self): return self.nome

# Modelo User
class User(AbstractUser):
    username = None  
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField('Email', unique=True)
    cpf = models.CharField('CPF', max_length=11, unique=True, validators=[cpf_validator])
    telefone = models.CharField('Telefone', max_length=15, blank=True, null=True, validators=[phone_validator])
    telefone_responsavel = models.CharField('Telefone', max_length=15, blank=True, null=True, validators=[phone_validator])
    nome = models.CharField('Nome completo', max_length=150, blank=True)
    data_nascimento = models.DateField('Data de nascimento', null=True, blank=True)
    pronomes = models.CharField('Pronomes', max_length=50, blank=True)

    # Documentos
    curriculo_lattes = models.URLField('Currículo Lattes', blank=True)
    documento_cpf = models.BinaryField(null=True, blank=True)
    documento_rg = models.BinaryField(null=True, blank=True)
    foto = models.BinaryField(null=True, blank=True)

    # Endereço
    cep = models.CharField(max_length=10, blank=True)
    rua = models.CharField(max_length=150, blank=True)
    bairro = models.CharField(max_length=100, blank=True)
    numero = models.CharField(max_length=10, blank=True)
    complemento = models.CharField(max_length=100, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True)
    comprovante_residencia = models.BinaryField(null=True, blank=True)

    # Diversidade
    raca = models.ForeignKey(Raca, on_delete=models.SET_NULL, null=True, blank=True)
    genero = models.ForeignKey(Genero, on_delete=models.SET_NULL, null=True, blank=True)
    deficiencias = models.ManyToManyField(Deficiencia, blank=True)
    autodeclaracao_racial = models.BinaryField(null=True, blank=True)
    comprovante_deficiencia = models.BinaryField(null=True, blank=True)

    # Escola
    nome_escola = models.CharField(max_length=150, blank=True)
    tipo_ensino = models.CharField(max_length=100, blank=True)
    cep_escola = models.CharField(max_length=10, blank=True)
    rua_escola = models.CharField(max_length=150, blank=True)
    bairro_escola = models.CharField(max_length=100, blank=True)
    numero_escola = models.CharField(max_length=10, blank=True)
    complemento_escola = models.CharField(max_length=100, blank=True)
    cidade_escola = models.CharField(max_length=100, blank=True)
    estado_escola = models.CharField(max_length=2, blank=True)
    telefone_escola = models.CharField(max_length=15, blank=True, validators=[phone_validator])
    telefone_responsavel_escola = models.CharField(max_length=15, blank=True, validators=[phone_validator])

    # Sistema
    password_needs_reset = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'cpf'
    REQUIRED_FIELDS = ['email']
    objects = UserManager()

    FUNCAO_CHOICES = [
        ('estudante', 'Estudante'),
        ('professora', 'Professora'),
        ('admin', 'Admin'),
        ('avaliadora', 'Avaliadora'),
    ]

    funcao = models.CharField(
        max_length=20, 
        choices=FUNCAO_CHOICES,
        null=False,
        blank=False,
        default='estudante'
    )

    def save(self, *args, **kwargs):
        is_new_user = self._state.adding
        super().save(*args, **kwargs)

        if is_new_user or self.pk and self.groups.count() == 0:
            self.sincronizar_grupo()

    def sincronizar_grupo(self):
        if self.funcao:
            grupos_funcao = [choice[0] for choice in self.FUNCAO_CHOICES]
            for grupo in self.groups.filter(name__in=grupos_funcao):
                self.groups.remove(grupo)
            grupo, _ = Group.objects.get_or_create(name=self.funcao)
            self.groups.add(grupo)

    def __str__(self):
        return self.email

    @property
    def roles(self):
        return list(self.groups.values_list('name', flat=True))

@receiver(m2m_changed, sender=User.groups.through)
def sincronizar_funcao(sender, instance, action, **kwargs):
    """
    Atualiza a função do usuário quando grupos são modificados
    via admin Django ou outras interfaces
    """
    # Apenas para ações que alteram a relação
    if action in ['post_add', 'post_remove', 'post_clear']:
        # Evita recursão infinita
        if hasattr(instance, '_atualizando_funcao'):
            return
            
        # Marca que estamos atualizando para evitar loop
        instance._atualizando_funcao = True
        
        try:
            grupos_funcao = [choice[0] for choice in User.FUNCAO_CHOICES]
            grupos_usuario = instance.groups.filter(name__in=grupos_funcao)
            
            if grupos_usuario.exists():
                # Usa o primeiro grupo de função encontrado
                grupo_principal = grupos_usuario.first().name
                if instance.funcao != grupo_principal:
                    instance.funcao = grupo_principal
                    # Salva sem disparar o save completo
                    User.objects.filter(pk=instance.pk).update(funcao=grupo_principal)
            elif instance.funcao:
                # Se não tem grupo mas tem função, limpa a função
                User.objects.filter(pk=instance.pk).update(funcao=None)
        finally:
            # Remove a marca de atualização
            del instance._atualizando_funcao

class HistoricoEscolar(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    historico_escolar = models.FileField("Upload do histórico escolar", null=True, blank=True)
    def __str__(self):
        return f"Histórico de {self.usuario.username}"

class Disciplina(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.nome

class Nota(models.Model):
    historico = models.ForeignKey(HistoricoEscolar, related_name='notas', on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    bimestre = models.PositiveSmallIntegerField("Bimestre", choices=[(1, '1º'), (2, '2º'), (3, '3º'), (4, '4º')])
    valor = models.DecimalField("Valor da Nota", max_digits=4, decimal_places=2, null=True, blank=True)
    
    class Meta:
        unique_together = ('historico', 'disciplina', 'bimestre')

    def __str__(self):
        return f"{self.disciplina.nome} - {self.bimestre}º Bimestre ({self.historico.usuario.username})"
