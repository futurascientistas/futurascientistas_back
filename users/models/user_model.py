import uuid
from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from futuras_cientistas import settings
from users.models.address_model import Endereco
from users.models.school_model import Escola
from users.models.utils_model import Deficiencia, Genero, Raca
from users.managers import UserManager
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from utils.utils import  cpf_validator, phone_validator

# Modelo User
class User(AbstractUser):
    username = None  
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField('Email', unique=True)
    cpf = models.CharField('CPF', max_length=11, unique=True, validators=[cpf_validator])
    telefone = models.CharField('Telefone', max_length=15, blank=True, null=True, validators=[phone_validator])
    telefone_responsavel = models.CharField('Telefone do responsável', max_length=15, blank=True, null=True, validators=[phone_validator])
    nome = models.CharField('Nome completo', max_length=150, blank=True)
    data_nascimento = models.DateField('Data de nascimento', null=True, blank=True)
    pronomes = models.CharField('Pronomes', max_length=50, blank=True)

    # Documentos
    curriculo_lattes = models.URLField('Currículo Lattes', blank=True)
    documento_cpf = models.BinaryField(null=True, blank=True, verbose_name='Documento CPF')
    documento_rg = models.BinaryField(null=True, blank=True, verbose_name='Documento RG')
    foto = models.BinaryField(null=True, blank=True, verbose_name='Foto')
    
    

    # Endereço
    endereco = models.ForeignKey(Endereco, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Endereço Pessoal", related_name='usuarios') 

    # Diversidade
    raca = models.ForeignKey(Raca, on_delete=models.SET_NULL, null=True, blank=True)
    genero = models.ForeignKey(Genero, on_delete=models.SET_NULL, null=True, blank=True)
    deficiencias = models.ManyToManyField(Deficiencia, blank=True)
    autodeclaracao_racial = models.BinaryField(null=True, blank=True, verbose_name='Autodeclaração racial')
    comprovante_deficiencia = models.BinaryField(null=True, blank=True, verbose_name='Comprovante de deficiência')

    # Escola
    escola = models.ForeignKey(Escola, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Escola", related_name='usuarios')

    # Sistema
    password_needs_reset = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Documentações para o drive
    drive_boletim_escolar = models.CharField(max_length=255, null=True, blank=True, verbose_name="ID do boletim escolar no Drive")
    drive_termo_autorizacao = models.CharField(max_length=255, null=True, blank=True, verbose_name="ID do termo de autorização no Drive")
    drive_rg_frente = models.CharField(max_length=255, null=True, blank=True, verbose_name="ID do RG (frente) no Drive")
    drive_rg_verso = models.CharField(max_length=255, null=True, blank=True, verbose_name="ID do RG (verso) no Drive")
    
    drive_cpf_anexo = models.CharField(max_length=255, null=True, blank=True, verbose_name="ID do CPF no Drive")
    drive_declaracao_vinculo = models.CharField(max_length=255, null=True, blank=True, verbose_name="ID da declaração de vínculo no Drive")
    drive_documentacao_comprobatoria_lattes = models.CharField(max_length=255, null=True, blank=True, verbose_name="ID da documentação Lattes no Drive")

    # Configurações do usuário
    termo_responsabilidade = models.BooleanField(default=False, verbose_name="Termo de responsabilidade")
    autodeclaracao = models.BooleanField(default=False, verbose_name="Declaração de veracidade das informações")
    
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
