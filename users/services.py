from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from .models import User

import random
import string
import re

from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import EmailValidator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.password_validation import validate_password

from .models import User
from .permissions import (
    IsAdminOrAvaliadora as IsAdminOrEvaluator,
    IsSelfOrAdminOrAvaliadora as IsOwnerOrAdminOrEvaluator,
)

def adicionar_usuario_ao_grupo(usuario: User, nome_grupo: str, operador: User):
    """
    Adiciona o usuário ao grupo especificado, se o operador for admin.
    Atualiza os grupos do usuário e garante consistência.
    """
    if not operador.is_staff:
        raise PermissionDenied("Somente admins podem alterar grupos de usuários.")

    grupo, created = Group.objects.get_or_create(name=nome_grupo)
    usuario.groups.add(grupo)
    usuario.save()  # salva para gatilhar lógica de default etc.

def remover_usuario_do_grupo(usuario: User, nome_grupo: str, operador: User):
    """
    Remove o usuário do grupo especificado, se o operador for admin.
    Se não restar grupo, adiciona o grupo 'estudante' automaticamente.
    """
    if not operador.is_admin:
        raise PermissionDenied("Somente admins podem alterar grupos de usuários.")

    try:
        grupo = Group.objects.get(name=nome_grupo)
    except Group.DoesNotExist:
        return  # ou raise um erro se preferir

    usuario.groups.remove(grupo)
    usuario.save()

    # Se não tiver mais grupo, adiciona estudante
    if not usuario.groups.exists():
        estudante, _ = Group.objects.get_or_create(name='estudante')
        usuario.groups.add(estudante)
        usuario.save()

def listar_membros_do_grupo(nome_grupo: str, operador: User):
    """
    Retorna queryset dos usuários que são membros do grupo,
    somente se operador for admin.
    """
    if not operador.is_admin:
        raise PermissionDenied("Somente admins podem listar membros de grupos.")

    try:
        grupo = Group.objects.get(name=nome_grupo)
    except Group.DoesNotExist:
        return User.objects.none()

    return grupo.user_set.all()

def validar_email(email):
    email_validator = EmailValidator()
    try:
        email_validator(email)
        return True
    except DjangoValidationError:
        return False


def validar_cpf(cpf: str) -> bool:
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    def calcular_digito(cpf_parcial, peso):
        soma = sum(int(digito) * p for digito, p in zip(cpf_parcial, peso))
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)

    primeiro_digito = calcular_digito(cpf[:9], range(10, 1, -1))
    segundo_digito = calcular_digito(cpf[:10], range(11, 1, -1))

    return cpf[-2:] == primeiro_digito + segundo_digito


def validar_senha(senha):
    try:
        validate_password(senha)
        return True
    except DjangoValidationError as e:
        return '; '.join(e.messages)


def gerar_senha_recuperacao(tamanho=12):
    caracteres = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    # Usa SystemRandom para maior segurança
    return ''.join(random.SystemRandom().choice(caracteres) for _ in range(tamanho))


def enviar_email_recuperacao(user, nova_senha):
    subject = 'Recuperação de Senha'
    from_email = 'no-reply@futurascientistas.com'
    to = [user.email]

    html_content = render_to_string('emails/recuperacao_senha.html', {
        'nome': user.nome,
        'nova_senha': nova_senha
    })
    text_content = f"Sua nova senha é: {nova_senha}"

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def encontrar_usuario_por_email_ou_cpf(email=None, cpf=None):
    if email:
        return User.objects.get(email=email)
    if cpf:
        cpf_limpo = re.sub(r'\D', '', cpf)
        return User.objects.get(cpf=cpf_limpo)
    raise ValueError("É necessário informar email ou CPF.")

def resetar_senha_usuario(user):
    nova_senha = gerar_senha_recuperacao()
    enviar_email_recuperacao(user, nova_senha)
    user.set_password(nova_senha)
    user.password_needs_reset = True
    user.save()
    return nova_senha

def get_valid_group(group_names):
    """
    Retorna o primeiro grupo válido da lista (que não seja 'admin' nem 'avaliadora').
    Se não houver válido, retorna o grupo 'estudante'.
    """
    if not group_names:
        return Group.objects.get_or_create(name='estudante')[0]

    if isinstance(group_names, (str, Group)):
        group_names = [group_names]

    for group in group_names:
        name = None
        if isinstance(group, Group):
            name = group.name.lower()
        elif isinstance(group, str):
            name = group.lower()

        if name and name not in ['admin', 'avaliadora']:
            grupo = Group.objects.filter(name__iexact=name).first()
            if grupo:
                return grupo

    return Group.objects.get_or_create(name='estudante')[0]