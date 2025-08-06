import re
import mimetypes
import magic

from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import viewsets, status, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponse
from django.views.generic.edit import FormView
from .forms import *
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import JsonResponse



from .services import *

from .serializers import UserSerializer
from .models import User
from .permissions import (
    IsAdminOrAvaliadora as IsAdminOrEvaluator,
    IsSelfOrAdminOrAvaliadora as IsOwnerOrAdminOrEvaluator,
    IsAdminRole
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrEvaluator]



class RecuperacaoSenhaAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        cpf = request.data.get('cpf')

        if not email and not cpf:
            return Response({'mensagem': 'Informe o CPF ou o email.'}, status=status.HTTP_400_BAD_REQUEST)

        if email and not validar_email(email):
            return Response({'mensagem': 'Email inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = encontrar_usuario_por_email_ou_cpf(email=email, cpf=cpf)
        except User.DoesNotExist:
            return Response({'mensagem': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({'mensagem': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if user.password_needs_reset:
            return Response({'mensagem': 'A senha já foi resetada recentemente. Verifique seu email.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            resetar_senha_usuario(user)
        except Exception as e:
            return Response({'mensagem': f'Erro ao enviar email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'mensagem': 'Senha recuperada com sucesso. Verifique seu email.'}, status=status.HTTP_200_OK)
    


class CadastroAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser] 

    def post(self, request):
        data = request.data.copy()

        email = data.get('email')
        cpf = re.sub(r'\D', '', data.get('cpf', ''))
        senha = data.get('password')

        if not data.get('nome') or not email or not senha or not cpf:
            return Response({'mensagem': 'Campos obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)

        if not validar_email(email):
            return Response({'mensagem': 'Email inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        if not validar_cpf(cpf):
            return Response({'mensagem': 'CPF inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        senha_valida = validar_senha(senha)
        if senha_valida is not True:
            return Response({'mensagem': senha_valida}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({'mensagem': 'Email já cadastrado.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(cpf=cpf).exists():
            return Response({'mensagem': 'CPF já cadastrado.'}, status=status.HTTP_400_BAD_REQUEST)

        data['cpf'] = cpf

        serializer = UserSerializer(data=data, context={"request": request})

        if serializer.is_valid():
            user = serializer.save()
            user.set_password(senha)
            user.is_active = True
            user.save()

            refresh = RefreshToken.for_user(user)
            return Response({
                'mensagem': 'Usuário cadastrado com sucesso.',
                'usuario': UserSerializer(user).data,
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class LoginThrottle(UserRateThrottle):
    rate = '4/min'


class LoginAPIView(APIView):
    throttle_classes = [LoginThrottle]
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        cpf = re.sub(r'\D', '', request.data.get('cpf', ''))
        senha = request.data.get('senha')

        if not cpf or not senha:
            return Response({'mensagem': 'Campos obrigatórios.'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=cpf, password=senha)

        if user is None:
            return Response({'mensagem': 'Credenciais inválidas.'}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token),
        }, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrEvaluator]

    def get_queryset(self):
        return User.objects.all()


class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrEvaluator]

    def get_object(self):
        if self.kwargs.get('pk'):
            return super().get_object()
        return self.request.user


class UserUpdateView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrEvaluator]
    parser_classes = [MultiPartParser, FormParser] 

    def get_object(self):
        return get_object_or_404(User, pk=self.kwargs.get('pk'))

    def perform_update(self, serializer):
        # Não permite alterar CPF via update
        serializer.validated_data.pop('cpf', None)
        # Apenas admins podem alterar grupos
        if not self.request.user.groups.filter(name='admin').exists():
            serializer.validated_data.pop('groups', None)
        serializer.save()


class UserDeleteView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrEvaluator]

    def get_object(self):
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        senha = request.data.get('senha')
        if not senha or not request.user.check_password(senha):
            return Response({'mensagem': 'Senha incorreta.'}, status=status.HTTP_400_BAD_REQUEST)

        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'mensagem': 'Conta excluída com sucesso.'}, status=status.HTTP_200_OK)


class UpdateMyUserView(generics.UpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        serializer.validated_data.pop('cpf', None)
        serializer.save()


class GetMyUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class GroupMembersAPIView(APIView):
    permission_classes = [IsAdminUser] 

    def get(self, request, group_name):
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            return Response({"detail": "Grupo não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        users = User.objects.filter(groups=group)
        users_data = [{"id": u.id, "email": u.email, "cpf": u.cpf} for u in users]
        return Response(users_data)


class UserListAPIView(APIView):
    permission_classes = [IsAdminUser]  

    def get(self, request):
        users = User.objects.all()
        data = [{"id": u.id, "email": u.email, "cpf": u.cpf, "roles": u.roles} for u in users]
        return Response(data)


class UserDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"detail": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user)
        return Response(serializer.data)
    

class GerenciarGrupoAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):

        user_id = request.data.get("user_id")
        nome_grupo = request.data.get("grupo")

        if not user_id or not nome_grupo:
            return Response({"detail": "Parâmetros 'user_id' e 'grupo' são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            usuario = User.objects.get(id=user_id)
            operador = request.user
            adicionar_usuario_ao_grupo(usuario, nome_grupo, operador)
        except User.DoesNotExist:
            return Response({"detail": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

        return Response({"detail": f"Usuário adicionado ao grupo '{nome_grupo}' com sucesso."}, status=status.HTTP_200_OK)

    def delete(self, request):
    
        user_id = request.data.get("user_id")
        nome_grupo = request.data.get("grupo")

        if not user_id or not nome_grupo:
            return Response({"detail": "Parâmetros 'user_id' e 'grupo' são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            usuario = User.objects.get(id=user_id)
            operador = request.user
            remover_usuario_do_grupo(usuario, nome_grupo, operador)
        except User.DoesNotExist:
            return Response({"detail": "Usuário não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

        return Response({"detail": f"Usuário removido do grupo '{nome_grupo}' com sucesso."}, status=status.HTTP_200_OK)
    

class AnexoDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, field_name):
        user = get_object_or_404(User, pk=user_id)

        if not request.user.is_superuser and request.user != user:
            return HttpResponse("Acesso negado", status=403)

        if not hasattr(user, field_name):
            return HttpResponse("Campo não encontrado", status=400)

        arquivo = getattr(user, field_name)
        if not arquivo:
            return HttpResponse("Arquivo não encontrado", status=404)

        if isinstance(arquivo, memoryview):
            arquivo = bytes(arquivo)

        try:
            mime = magic.Magic(mime=True)
            mime_type = mime.from_buffer(arquivo)
        except Exception:
            mime_type = "application/octet-stream"

        ext = mimetypes.guess_extension(mime_type) or ".bin"

        filename = f"{field_name}{ext}"

        response = HttpResponse(arquivo, content_type=mime_type)
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
    
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, field_name):
        user = get_object_or_404(User, pk=user_id)

        if not request.user.is_superuser and request.user != user:
            return JsonResponse({'erro': 'Acesso negado.'}, status=403)

        if not hasattr(user, field_name):
            return JsonResponse({'erro': f"Campo '{field_name}' não encontrado."}, status=400)

        arquivo = getattr(user, field_name)
        if not arquivo:
            return JsonResponse({'status': 'Vazio'}, status=204)

        if isinstance(arquivo, memoryview):
            arquivo = bytes(arquivo)

        try:
            mime = magic.Magic(mime=True)
            mime_type = mime.from_buffer(arquivo)
        except Exception as e:
            return JsonResponse({'erro': f'Erro ao detectar MIME: {str(e)}'}, status=500)

        return JsonResponse({
            'campo': field_name,
            'tamanho_bytes': len(arquivo),
            'mime_type': mime_type,
            'tipo_arquivo': 'Possível PDF' if mime_type == 'application/pdf' else 'Outro',
        })
    

class CadastroView(FormView):
    template_name = "components/users/registration_form.html"
    form_class = CadastroForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        data = form.cleaned_data
        email = data['email']
        cpf = re.sub(r'\D', '', data['cpf'])
        senha = data['password']
        nome = data['nome']

        if User.objects.filter(email=email).exists():
            form.add_error('email', 'Email já cadastrado.')
            return self.form_invalid(form)

        if User.objects.filter(cpf=cpf).exists():
            form.add_error('cpf', 'CPF já cadastrado.')
            return self.form_invalid(form)

        user = User(nome=nome, email=email, cpf=cpf)
        user.set_password(senha)
        user.is_active = True
        user.save()
        messages.success(self.request, "Usuário cadastrado com sucesso!")
        return super().form_valid(form)

def login_view(request):
    if request.method == 'POST':
        cpf = request.POST.get('cpf')
        senha = request.POST.get('senha')
        user = authenticate(request, username=cpf, password=senha)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # ou outra página interna
        else:
            messages.error(request, 'CPF ou senha inválidos.')

    return render(request, 'components/users/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    user_roles = getattr(request.user, 'roles', []) 
    print("Grupos do usuário:", user_roles) 

    menu_items = [
        {
            "id": "cadastro",
            "title": "Criar projeto",
            "roles": ["admin", "tutor"],
            "url": "/project",
            "icon_svg": """
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 5v14m-7-7h14"/>
                </svg>
            """
        },
        {
            "id": "lista_projetos",
            "title": "Lista de Projetos",
            "roles": ["admin", "tutor"],
            "url": "/project-list",
            "icon_svg": """
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2"/>
                <path d="M3 10h18"/>
                </svg>
            """
        },
        {
            "id": "inscricao_aluna",
            "title": "Minha Inscrição",
            "roles": ["estudante"],
            "url": "/inscricao-aluna",
            "icon_svg": """
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="7" r="4"/>
                <path d="M5.5 21h13a2 2 0 0 0-13 0z"/>
                </svg>
            """
        },
        {
            "id": "projetos_disponiveis",
            "title": "Projetos Disponíveis",
            "roles": ["estudante"],
            "url": "/projetos-disponiveis",
            "icon_svg": """
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 21v-2a4 4 0 0 1 4-4h8a4 4 0 0 1 4 4v2"/>
                <rect x="2" y="2" width="20" height="16" rx="2" ry="2"/>
                </svg>
            """
        },
        {
            "id": "cronograma",
            "title": "Cronograma",
            "roles": [],  # visível para todos
            "url": "/dashboard/cronograma",
            "icon_svg": """
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="4" width="18" height="18" rx="2"/>
                <line x1="16" y1="2" x2="16" y2="6"/>
                <line x1="8" y1="2" x2="8" y2="6"/>
                <line x1="3" y1="10" x2="21" y2="10"/>
                </svg>
            """
        },
        {
            "id": "avaliacao",
            "title": "Avaliação de inscrição",
            "roles": ["admin"],
            "url": "/dashboard/avaliacao",
            "icon_svg": """
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polygon points="12 2 15 8 22 9 17 14 18 21 12 18 6 21 7 14 2 9 9 8 12 2"/>
                </svg>
            """
        },
        {
            "id": "notificacoes",
            "title": "Notificações",
            "roles": [],  # visível para todos
            "url": "/dashboard/notificacoes",
            "icon_svg": """
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/>
                <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
                </svg>
            """
        },
        {
            "id": "frequencia",
            "title": "Frequência",
            "roles": [],  # admin e tutor
            "url": "/dashboard/frequencia",
            "icon_svg": """
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 3v18h18"/>
                <path d="M7 17l4-4 3 3 4-7"/>
                </svg>
            """
        },
        {
            "id": "indicadores",
            "title": "Indicadores",
            "roles": [],  # admin e tutor
            "url": "/dashboard/indicadores",
            "icon_svg": """
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 20V10"/>
                <path d="M18 20V4"/>
                <path d="M6 20v-6"/>
                </svg>
            """
        },
        {
            "id": "analise",
            "title": "Análise de relatórios (TCC)",
            "roles": [],  # admin e tutor
            "url": "/dashboard/analise",
            "icon_svg": """
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 4h16v16H4z"/>
                <path d="M4 9h16"/>
                <path d="M9 20V9"/>
                </svg>
            """
        },
        {
            "id": "dados",
            "title": "Dados de projetos",
            "roles": ["admin", "tutor"],
            "url": "/dashboard/dados",
            "icon_svg": """
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <path d="M3 9h18"/>
                <path d="M9 21V9"/>
                </svg>
            """
        },
        {
            "id": "logout",
            "title": "Sair",
            "roles": [],  # todos podem ver
            "url": "/logout",
            "icon_svg": """
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                <polyline points="16 17 21 12 16 7"/>
                <line x1="21" y1="12" x2="9" y2="12"/>
                </svg>
            """
        },
    ]


    filtered_items = [
        item for item in menu_items
        if any(role in item["roles"] for role in user_roles)
    ]

    context = {
        "menu_items": filtered_items,
        "active_item": "cadastro",
        "user": request.user,
        "user_roles": user_roles,
    }
    return render(request, "components/dashboard/sidebar/dashboard.html", context)

@login_required
def perfil_view(request):
    user = request.user

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('perfil')  
    else:
        form = UserUpdateForm(instance=user)



    return render(request, 'components/users/perfil.html', {'form': form})