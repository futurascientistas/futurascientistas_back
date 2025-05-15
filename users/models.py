from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, cpf, email, nome, senha=None):
        if not cpf:
            raise ValueError("O usuário precisa de um CPF")
        if not email:
            raise ValueError("O usuário precisa de um email")

        user = self.model(
            cpf=cpf,
            email=self.normalize_email(email),
            nome=nome
        )
        user.set_password(senha)
        user.save(using=self._db)
        return user

    def create_superuser(self, cpf, email, nome, senha):
        user = self.create_user(cpf, email, nome, senha)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, blank=False, null=False)
    nome = models.CharField(max_length=100, blank=False, null=False)
    cpf = models.CharField(max_length=11, unique=True, blank=False, null=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    password_needs_reset = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'cpf'  
    REQUIRED_FIELDS = ['email', 'nome']  
    def __str__(self):
        return self.cpf
