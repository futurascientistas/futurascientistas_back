from django.contrib.auth.models import AbstractUser, BaseUserManager, Group
from django.db import models
from django.core.validators import RegexValidator, FileExtensionValidator
import uuid
from .managers import UserManager

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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.groups.exists():
            estudante_group, _ = Group.objects.get_or_create(name='estudante')
            self.groups.add(estudante_group)

    def __str__(self):
        return self.email
