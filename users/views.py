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

class RecuperacaoSenhaAPIView(APIView):
  permission_classes = [permissions.AllowAny]
  
  def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({'mensagem': 'Email é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'mensagem': 'Email não encontrado'}, status=status.HTTP_400_BAD_REQUEST)

        nova_senha = gerar_senha_recuperacao()

        user.set_password(nova_senha)
        user.save()

        send_mail(
            'Recuperação de Senha',  
            f'Sua nova senha é: {nova_senha}', 
            'no-reply@seusite.com',  
            [user.email], 
            fail_silently=False, 
        )

        return Response({'mensagem': 'Senha recuperada com sucesso. Verifique seu email.'}, status=status.HTTP_200_OK)

class CadastroAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        nome = request.data.get('nome')
        email = request.data.get('email')
        senha = request.data.get('senha')

        if not nome or not email or not senha:
            return Response({'mensagem': 'Campos obrigatórios'}, status=status.HTTP_400_BAD_REQUEST)

        if not validar_email(email):
            return Response({'mensagem': 'Email inválido'}, status=status.HTTP_400_BAD_REQUEST)

        senha_valida = validar_senha(senha)
        if senha_valida != True:
            return Response({'mensagem': senha_valida}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'mensagem': 'Email já cadastrado'}, status=status.HTTP_400_BAD_REQUEST)

        user = User(nome=nome, email=email)
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

class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        senha = request.data.get('senha')

        if not email or not senha:
            return Response({'mensagem': 'Campos obrigatórios'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=email, password=senha)

        if user is None:
            return Response({'mensagem': 'Credenciais inválidas'}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({
            'refresh_token': str(refresh),
            'access_token': access_token,
        }, status=status.HTTP_200_OK)


