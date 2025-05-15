import hashlib

from .models import User
from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from rest_framework.throttling import UserRateThrottle
import random
import string
import re

def validar_email(email):
    email_validator = EmailValidator()
    try:
        email_validator(email)
    except ValidationError:
        return False
    return True

def validar_cpf(cpf: str) -> bool:
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    def calcular_digito(cpf, peso):
        soma = sum(int(digito) * p for digito, p in zip(cpf, peso))
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)

    primeiro_digito = calcular_digito(cpf[:9], range(10, 1, -1))
    segundo_digito = calcular_digito(cpf[:10], range(11, 1, -1))

    return cpf[-2:] == primeiro_digito + segundo_digito


def validar_senha(senha):
    # Verificar se a senha tem entre 8 e 12 caracteres
    if len(senha) < 8 or len(senha) > 12:
        return "A senha deve ter entre 8 e 12 caracteres."

    # Verificar se a senha tem pelo menos uma letra maiúscula
    if not re.search(r'[A-Z]', senha):
        return "A senha deve conter pelo menos uma letra maiúscula."

    # Verificar se a senha tem pelo menos um número
    if not re.search(r'[0-9]', senha):
        return "A senha deve conter pelo menos um número."

    # Verificar se a senha tem pelo menos um caractere especial
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', senha):
        return "A senha deve conter pelo menos um caractere especial."

    return True

def gerar_senha_recuperacao(tamanho=12):

    caracteres = string.ascii_letters + string.digits + string.punctuation
    senha = ''.join(random.choice(caracteres) for _ in range(tamanho))

    return senha

def enviar_email_recuperacao(user, nova_senha):
    subject = 'Recuperação de Senha'
    from_email = 'no-reply@futurascientistas.com'
    to = [user.email]

    html_content = render_to_string('emails/recuperacao_senha.html', {
    'nome': user.nome,
    'nova_senha': nova_senha
    })
    text_content = f"Sua nova senha é: {nova_senha}"  # Para e-mails que não suportam HTML

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()
  
  
class RecuperacaoSenhaAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        cpf = request.data.get('cpf')

        if not email and not cpf:
            return Response({'mensagem': 'Informe o CPF ou o email.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if email:
                user = User.objects.get(email=email)
            else:
               
                cpf_limpo = re.sub(r'\D', '', cpf)
                user = User.objects.get(cpf=cpf_limpo)
        except User.DoesNotExist:
            return Response({'mensagem': 'Usuário não encontrado.'}, status=status.HTTP_400_BAD_REQUEST)

        if user.password_needs_reset:
            return Response({'mensagem': 'A senha já foi resetada recentemente. Verifique seu email.'}, status=status.HTTP_400_BAD_REQUEST)

        nova_senha = gerar_senha_recuperacao()
        try:
            enviar_email_recuperacao(user, nova_senha)
        except Exception as e:
            return Response({'mensagem': f'Erro ao enviar email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        user.set_password(nova_senha)
        user.password_needs_reset = True
        user.save()

        return Response({'mensagem': 'Senha recuperada com sucesso. Verifique seu email.'}, status=status.HTTP_200_OK)


class CadastroAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        nome = request.data.get('nome')
        email = request.data.get('email')
        cpf = request.data.get('cpf')
        cpf = re.sub(r'\D', '', cpf) 
        senha = request.data.get('senha')

        if not nome or not email or not senha or not cpf:
            return Response({'mensagem': 'Campos obrigatórios'}, status=status.HTTP_400_BAD_REQUEST)

        if not validar_email(email):
            return Response({'mensagem': 'Email inválido'}, status=status.HTTP_400_BAD_REQUEST)

        if not validar_cpf(cpf):
            return Response({'mensagem': 'CPF inválido'}, status=status.HTTP_400_BAD_REQUEST)

        senha_valida = validar_senha(senha)
        if senha_valida != True:
            return Response({'mensagem': senha_valida}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'mensagem': 'Email já cadastrado'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(cpf=cpf).exists():
            return Response({'mensagem': 'CPF já cadastrado'}, status=status.HTTP_400_BAD_REQUEST)

        user = User(nome=nome, email=email, cpf=cpf)
        user.set_password(senha)
        user.save()  

        serializer = UserSerializer(user)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({
            'mensagem': 'Usuário cadastrado com sucesso',
            'usuario': serializer.data,
            'access_token': access_token,
            'refresh_token': str(refresh),
        }, status=status.HTTP_201_CREATED)

class LoginThrottle(UserRateThrottle):
    rate = '4/min'  # 4 tentativas por minturs

class LoginAPIView(APIView):
    throttle_classes = [LoginThrottle]
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        cpf = request.data.get('cpf')
        senha = request.data.get('senha')
        cpf = re.sub(r'\D', '', cpf) 

        if not cpf or not senha:
            return Response({'mensagem': 'Campos obrigatórios'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=cpf, password=senha)

        if user is None:
            return Response({'mensagem': 'Credenciais inválidas'}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({
            'refresh_token': str(refresh),
            'access_token': access_token,
        }, status=status.HTTP_200_OK)


