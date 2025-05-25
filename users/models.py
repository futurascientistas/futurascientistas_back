# models.py
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid

ROLES = [
    ('estudante', 'Estudante'),
    ('professor', 'Professor'),
    ('admin', 'Administrador'),
    ('avaliadora', 'Avaliadora'),
]

class UserManager(BaseUserManager):
    def create_user(self, cpf, email, nome, senha=None):
        if not cpf:
            raise ValueError("O usuário precisa de um CPF")
        if not email:
            raise ValueError("O usuário precisa de um email")

        email = self.normalize_email(email)
        user = self.model(
            cpf=cpf,
            email=email,
            nome=nome
        )
        user.set_password(senha)
        user.save(using=self._db)
        return user

    def create_superuser(self, cpf, email, nome, senha):
        user = self.create_user(cpf, email, nome, senha)
        user.is_staff = True
        user.is_superuser = True
        user.role = 'admin'
        user.save(using=self._db)

        from django.contrib.auth.models import Group
        admin_group, _ = Group.objects.get_or_create(name='admin')
        user.groups.add(admin_group)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    nome = models.CharField(max_length=100, blank=False, null=False)
    cpf = models.CharField(max_length=11, unique=True, blank=False, null=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=ROLES, default='estudante', verbose_name='Função')
    bio = models.TextField(blank=True, null=True, verbose_name='Biografia')
    birth_date = models.DateField(blank=True, null=True, verbose_name='Data de Nascimento')

    password_needs_reset = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'cpf'
    REQUIRED_FIELDS = ['email', 'nome']

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f"{self.nome} ({self.email})"

    def save(self, *args, **kwargs):
        grupos = self.groups.all()
        if grupos.exists():
            novo_role = grupos.first().name
            if self.role != novo_role:
                self.role = novo_role
        else:
            if not self.role:
                self.role = 'estudante'

        if self.role == 'admin':
            self.is_staff = True
            self.is_superuser = True
        else:
            self.is_staff = False
            self.is_superuser = False

        super().save(*args, **kwargs)

        group, _ = Group.objects.get_or_create(name=self.role)
        if group not in self.groups.all():
            self.groups.clear()
            self.groups.add(group)


class Genero(models.Model):
    nome = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nome
