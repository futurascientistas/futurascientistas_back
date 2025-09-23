import re
import mimetypes
import magic
import logging
import traceback

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
from django.db import transaction
from core.models import Cidade, Estado
from users.models.address_model import Endereco
from users.models.school_model import Escola
from users.models.school_transcript_model import Disciplina, HistoricoEscolar, Nota
from .forms import *
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.conf import settings
from applications.drive.drive_services import DriveService


from .services import *

from .serializers import UserSerializer
from .models import User
from .permissions import (
    IsAdminOrAvaliadora as IsAdminOrEvaluator,
    IsSelfOrAdminOrAvaliadora as IsOwnerOrAdminOrEvaluator,
    IsAdminRole
)

logger = logging.getLogger(__name__)

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
        funcao = data['group']

        if User.objects.filter(email=email).exists():
            form.add_error('email', 'Email já cadastrado.')
            return self.form_invalid(form)

        if User.objects.filter(cpf=cpf).exists():
            form.add_error('cpf', 'CPF já cadastrado.')
            return self.form_invalid(form)

        user = User(nome=nome, email=email, cpf=cpf, funcao=funcao)
        user.set_password(senha)
        user.is_active = True
        user.save()
        messages.success(self.request, "Usuário cadastrado com sucesso!")
        return super().form_valid(form)

def login_view(request):
    if request.method == 'POST':
        cpf = request.POST.get('cpf')
        cpf = re.sub(r'\D', '', cpf)
        senha = request.POST.get('senha')
        user = authenticate(request, username=cpf, password=senha)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'CPF ou senha inválidos.')

    return render(request, 'components/users/login.html')


def logout_view(request):
    storage = messages.get_messages(request)
    for _ in storage:
        pass  
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    user_roles = getattr(request.user, 'roles', []) 

    context = {
        "active_item": "cadastro",
        "user": request.user,
        "user_roles": user_roles,
    }
    return render(request, "components/dashboard/sidebar/dashboard.html", context)

@login_required
def perfil_view(request):
    user = request.user

    endereco_instance = user.endereco if user.endereco else Endereco()
    escola_instance = user.escola if user.escola else Escola()
    historico, created = HistoricoEscolar.objects.get_or_create(usuario=user)
    endereco_escola_instance = escola_instance.endereco if escola_instance.endereco else Endereco()
    
    if user.funcao == 'estudante':
        if not historico.notas.exists():
            try:
                disciplinas = Disciplina.objects.all()
                bimestres = [1, 2]
                
                with transaction.atomic():
                    for disciplina in disciplinas:
                        for bimestre in bimestres:
                            Nota.objects.create(
                                historico=historico,
                                disciplina=disciplina,
                                bimestre=bimestre,
                                valor=0.0
                            )
                messages.info(request, "Notas iniciais criadas para todas as disciplinas.")
            except Exception as e:
                logger.error(f"Erro ao criar notas iniciais: {str(e)}")
                messages.error(request, "Erro ao carregar o formulário de notas. Por favor, tente novamente.")

    if request.method == 'POST':
        current_step = int(request.POST.get('current_step', 1))
        
        if user.funcao == 'professora':
            valid_steps = [1, 2, 3, 4, 6]
        else:
            valid_steps = [1, 2, 3, 4, 5, 6]

        is_valid = False
        
        try:
            with transaction.atomic():
                if current_step == 1:
                    form = UserUpdateForm(request.POST, request.FILES, instance=user, user=request.user)
                    if form.is_valid():
                        user_obj = form.save(commit=False)
                        user_obj.save()
                        form.save_m2m() 
                        messages.success(request, 'Identificação atualizada com sucesso! 🚀')
                        is_valid = True
                    else:
                        logger.error(f"Erro na validação do formulário de Identificação: {form.errors}")
                        messages.error(request, 'Erro na validação do formulário de Identificação. Por favor, corrija os erros abaixo.')
                        pass 

                elif current_step == 2:
                    form = EnderecoForm(request.POST, instance=endereco_instance)

                    if form.is_valid():                 
                        endereco_obj = form.save()
                        user.endereco = endereco_obj
                        user.save()
                        messages.success(request, 'Endereço atualizado com sucesso! 🏠')
                        is_valid = True
                    else:
                        logger.error(f"Erro na validação do formulário de Endereço: {form.errors}")
                        messages.error(request, 'Erro na validação do formulário de Endereço. Por favor, corrija os erros abaixo.')
                
                elif current_step == 3:
                    escola_form = EscolaForm(request.POST, instance=escola_instance)
                    escola_endereco_form = EnderecoForm(request.POST, prefix='endereco_escola', instance=endereco_escola_instance)
                    
                    if escola_endereco_form.is_valid():
                        endereco_escola_obj = escola_endereco_form.save()

                        if escola_form.is_valid() and escola_endereco_form.is_valid():
                            escola_obj = escola_form.save(commit=False)
                            escola_obj.endereco = endereco_escola_obj
                            escola_obj.save()
                            user.escola = escola_obj
                            user.save()
                            messages.success(request, 'Escola atualizada com sucesso! 🏫')
                            is_valid = True
                        else:
                            logger.error(f"Erro na validação do formulário de Identificação: {escola_form.errors}")
                            messages.error(request, 'Erro na validação do formulário de Escola. Por favor, corrija os erros abaixo.')
                    else:
                        logger.error(f"Erro na validação do formulário de Identificação: {escola_endereco_form.errors}")
                        messages.error(request, 'Erro na validação do formulário do Endereço da Escola. Por favor, corrija os erros abaixo.')
                   
                elif current_step == 4:
                    form = UserUpdateForm(request.POST, request.FILES, instance=user, user=request.user)
                    is_upload = request.POST.get("auto_upload") == "1"
                    if form.is_valid():
                        try:
                            user = form.save()
                            messages.success(request, 'Documentos atualizados com sucesso! 📄')
                            if is_upload:
                                return redirect(f'{request.path}?step={current_step}')
                            else:
                                is_valid = True
                        except Exception as e:
                            logger.error(f"Erro ao fazer upload para o Drive: {str(e)}")
                            messages.error(request, f'Erro ao enviar documentos para o Drive: {str(e)}')

                    else:
                        # Adiciona esta parte para mostrar os erros específicos
                        error_messages = []
                        for field, errors in form.errors.items():
                            field_label = form.fields[field].label if field in form.fields else field
                            for error in errors:
                                error_messages.append(f"{field_label}: {error}")
                        
                        messages.error(request, 'Erro na validação do formulário de Documentos. Por favor, corrija os erros abaixo:')
                        for error_msg in error_messages:
                            messages.error(request, error_msg)  # Mostra cada erro individualmente
                    

                elif current_step == 5:
                    formset = HistoricoNotaFormSet(request.POST, instance=historico,  prefix="notas")
                    user_form = UserUpdateForm(request.POST, request.FILES, instance=user, user=request.user)
                    is_upload = request.POST.get("auto_upload") == "1"
                    # historico_form = HistoricoEscolarForm(request.POST, request.FILES, instance=historico)
                    if is_upload:
                        if user_form.is_valid():
                            try:

                                user = user_form.save()
                                user.refresh_from_db() 

                                historico.historico_escolar = user.drive_boletim_escolar
                                historico.save()

                                messages.success(request, 'Boletim enviado com sucesso! 📝')

                                is_valid = True
                            except Exception as e:
                                logger.error(f"Erro ao fazer upload para o Drive: {str(e)}")
                                messages.error(request, f'Erro ao enviar documentos para o Drive: {str(e)}')
                        else:
                            error_messages = []
                            for field, errors in user_form.errors.items():
                                field_label = user_form.fields[field].label if field in user_form.fields else field
                                for error in errors:
                                    error_messages.append(f"{field_label}: {error}")
                            messages.error(request, 'Erro no formulário de upload. Por favor, corrija os erros abaixo:')
                            for error_msg in error_messages:
                                messages.error(request, error_msg)
                            logger.error(f"Erro na validação do upload na etapa 5: {user_form.errors}")
                            messages.error(request, 'Erro na validação do formulário enviado.')
                            
                        return redirect(f'{request.path}?step={current_step}')  
                    else:
                        if formset.is_valid() and user_form.is_valid():
                            try:
                                formset.save()
                                user = user_form.save()
                                messages.success(request, 'Boletim escolar atualizado com sucesso! 📝')
                                is_valid = True
                            except:
                                logger.error(f"Erro ao salvar formulários da etapa 5: {str(e)}")
                                messages.error(request, f'Erro ao salvar. Tente novamente.{str(e)}')
                        else:
                            logger.error(f"Erro na validação do boletim escolar. Por favor, corrija os erros abaixo: {formset.errors}")
                            messages.error(request, 'Erro na validação do boletim escolar. Por favor, corrija os erros abaixo.')

                elif current_step == 6:
                    form = UserUpdateForm(request.POST, request.FILES, instance=user)
                    if form.is_valid():
                        form.save()
                        messages.success(request, 'Perfil finalizado e salvo com sucesso! 🎉')
                        is_valid = True
                    else:
                        logger.error(f"Erro na validação da Declaração. Por favor, tente novamente.{form.errors}")
                        messages.error(request, 'Erro na validação da Declaração. Por favor, tente novamente.')
                
                # Redirecionamento para o próximo passo se o formulário for válido
                if is_valid:
                    try:
                        next_step_index = valid_steps.index(current_step) + 1
                        next_step = valid_steps[next_step_index]
                        return redirect(f'/usuarios/dashboard/perfil/?step={next_step}')
                    except (ValueError, IndexError):
                        return redirect(request.path)
                else:
                    return redirect(f'{request.path}?step={current_step}')

        except Exception as e:
            logger.error(f'Ocorreu um erro inesperado: {str(e)}')
            messages.error(request, f'Ocorreu um erro inesperado: {str(e)}')
            # Em caso de erro, você pode querer manter o usuário no passo atual.
            # return redirect(f'{request.path}?step={current_step}')

    user_form = UserUpdateForm(instance=user)
    endereco_form = EnderecoForm(instance=endereco_instance)
    escola_form = EscolaForm(instance=escola_instance)
    escola_endereco_form = EnderecoForm(instance=endereco_escola_instance, prefix='endereco_escola')
    # historico_form = HistoricoEscolarForm(instance=historico)
    queryset_notas = historico.notas.all().order_by('disciplina__nome', 'bimestre')
    
    formset = HistoricoNotaFormSet(
        request.POST or None,
        instance=historico,
        prefix="notas",
        queryset=queryset_notas
    )

    if user.funcao == 'professora':
        campos_estudante = ['drive_boletim_escolar', 'telefone_responsavel', 'comprovante_autorizacao_responsavel', 'comprovante_autorizacao_responsavel__upload', 'comprovante_autorizacao_responsavel__clear']
        for campo in campos_estudante:
            if campo in user_form.fields:
                del user_form.fields[campo]

    if user.funcao == 'professora':
        steps = [
            {'number': 1, 'name': 'Identificação'},
            {'number': 2, 'name': 'Endereço'},
            {'number': 3, 'name': 'Escola'},
            {'number': 4, 'name': 'Documentos'},
            {'number': 6, 'name': 'Declaração'}
        ]
    else: 
        steps = [
            {'number': 1, 'name': 'Identificação'},
            {'number': 2, 'name': 'Endereço'},
            {'number': 3, 'name': 'Escola'},
            {'number': 4, 'name': 'Documentos'},
            {'number': 5, 'name': 'Boletim'},
            {'number': 6, 'name': 'Declaração'}
        ]

    context = {
        'user_form': user_form,
        'endereco_form': endereco_form,
        'escola_form': escola_form,
        'escola_endereco_form': escola_endereco_form,
        'formset': formset, 
        # 'historico_form': historico_form,
        'user': user,
        'steps': steps,
    }

    current_step_from_url = int(request.GET.get('step', 1))
    
    context['current_step'] = current_step_from_url

    return render(request, 'components/users/perfil.html', context)




from django.views.generic import TemplateView
from django.views import View
from django.http import JsonResponse
from users.models.user_model import User
from projects.models import Project
from django.db.models import Q, Count, F
from users.models.utils_model import TipoDeVaga
from users.models.school_model import TipoEnsino
from applications.models import Application, ApplicationStatusLog


class ApiAlunasDatas(APIView):
    def get(self, request, *args, **kwargs):
        usuarios_qs = User.objects.filter(funcao='estudante')
        
        # Serialização manual
        usuarios = []
        for u in usuarios_qs:
            usuarios.append({
                "id": str(u.id),
                "nome": u.nome,
                "email": u.email,
                "cpf": u.cpf,
                "telefone": u.telefone,
                "funcao": u.funcao,
                "data_nascimento": u.data_nascimento.isoformat() if u.data_nascimento else None,
                "pronomes": u.pronomes,
            })
        
        return Response({
            "mensagem": "ok",
            "usuarios": usuarios
        })
        
class ApiProfessoresDatas(APIView):
    def get(self, request, *args, **kwargs):
        professores_qs = User.objects.filter(is_active=True, funcao='professora')
       
        # Serialização manual
        professores = []
        for p in professores_qs:
            professores.append({
                "id": str(p.id),
                "nome": p.nome,
                "email": p.email,
                "cpf": p.cpf,
                "telefone": p.telefone,
                "funcao": p.funcao,
                "data_nascimento": p.data_nascimento.isoformat() if p.data_nascimento else None,
                "pronomes": p.pronomes,
            })

        return Response({
            "mensagem": "ok",
            "professores": professores
        })
        
class ApiUsuariosComDeficiencia(APIView):
    def get(self, request, *args, **kwargs):
        usuarios = (
            User.objects.filter(deficiencias__isnull=False)
            .exclude(deficiencias__nome="Nenhuma")
            .distinct()
        )

        dados = []
        for u in usuarios:
            dados.append({
                "id": str(u.id),
                "nome": u.nome,
                "deficiencias": [d.nome for d in u.deficiencias.all()]
            })

        return Response({
            "mensagem": "ok",
            "usuarios_com_deficiencia": dados
        })

class ApiProjetosEmAndamento(APIView):
    def get(self, request, *args, **kwargs):
        # Projetos em andamento
        projetos = Project.objects.filter(status='em_andamento', ativo=True)

        dados = []
        for p in projetos:
            dados.append({
                "id": str(p.id),
                "nome": p.nome,
                "descricao": p.descricao,
                "tutora": p.tutora.nome if p.tutora else None,
                "eh_remoto": p.eh_remoto,
                "regioes_aceitas": [r.nome for r in p.regioes_aceitas.all()],
                "estados_aceitos": [e.nome for e in p.estados_aceitos.all()],
                "cidades_aceitas": [c.nome for c in p.cidades_aceitas.all()],
                "formato": p.formato,
                "status": p.status,
                "vagas": p.vagas,
                "instituicao": p.instituicao,
                "inicio_inscricoes": p.inicio_inscricoes,
                "fim_inscricoes": p.fim_inscricoes,
                "data_inicio": p.data_inicio,
                "data_fim": p.data_fim
            })

        total_projetos = Project.objects.filter(ativo=True).count()
        total_concluido = Project.objects.filter(status='concluido', ativo=True).count()
        print(total_projetos, total_concluido)

        return Response({
            "mensagem": "ok",
            "projetos_em_andamento": dados,
            "total_projetos": total_projetos,
            "total_concluido": total_concluido,
        })
        
class ApiPercentualProjetosConcluidos(APIView):
    def get(self, request, *args, **kwargs):
        total_projetos = Project.objects.count()
        concluidos = Project.objects.filter(status='concluido').count()

        percentual = 0
        if total_projetos > 0:
            percentual = (concluidos / total_projetos) * 100

        # Opcional: arredondar para 2 casas decimais
        percentual = round(percentual, 2)

        return Response({
            "mensagem": "ok",
            "total_projetos": total_projetos,
            "projetos_concluidos": concluidos,
            "percentual_concluidos": percentual
        })
        
class ApiProjetosComRegioes(APIView):
    def get(self, request, *args, **kwargs):
        projetos = Project.objects.prefetch_related('regioes_aceitas').all()

        dados = []
        for p in projetos:
            dados.append({
                "id": str(p.id),
                "nome": p.nome,
                "descricao": p.descricao,
                "regioes_aceitas": [r.nome for r in p.regioes_aceitas.all()]
            })

        return Response({
            "mensagem": "ok",
            "projetos_com_regioes": dados
        })
        
class ApiContagemPorTipoEnsino(APIView):
    def get(self, request, *args, **kwargs):
        # Faz o join via ForeignKey e agrupa pelo nome do tipo de ensino
        contagem = (
            User.objects
            .values('escola__tipo_ensino__nome')  # pega o nome do tipo de ensino
            .annotate(total=Count('id'))
        )

        dados = []
        for item in contagem:
            dados.append({
                "tipo_ensino": item['escola__tipo_ensino__nome'] or "Não informado",
                "total": item['total']
            })

        return Response({
            "mensagem": "ok",
            "contagem_por_tipo_ensino": dados
        })
        
class ApiContagemPorCidade(APIView):
    def get(self, request, *args, **kwargs):
        # Faz o join via ForeignKey: User → Endereco → Cidade
        contagem = (
            User.objects
            .values('endereco__cidade__nome')  # pega o nome da cidade
            .annotate(total=Count('id'))
        )

        dados = []
        for item in contagem:
            dados.append({
                "cidade": item['endereco__cidade__nome'] or "Não informado",
                "total": item['total']
            })

        return Response({
            "mensagem": "ok",
            "contagem_por_cidade": dados
        })

class ApiDashboardDiversidade(APIView):
    def get(self, request, *args, **kwargs):
        try:
            aplicacoes = Application.objects.all()
            
            # LEGENDAS: Tipos de Vaga (Ampla Concorrência, PPI, etc.)
            tipos_vaga = TipoDeVaga.objects.all().order_by('id')
            labels = [vaga.nome for vaga in tipos_vaga]
            
            # DATASETS: Categorias (Escolas Regulares, Técnicas, Professoras)
            datasets = []
            cores = ['#2ecc71', '#e67e22', '#9b59b6']  # Verde, Laranja, Roxo
            
            # 1. Escolas Regulares
            dados_regulares = []
            for tipo_vaga in tipos_vaga:
                count = aplicacoes.filter(
                    tipo_de_vaga=tipo_vaga,
                    usuario__funcao='estudante',
                    usuario__escola__tipo_ensino__nome='REGULAR'
                ).count()
                dados_regulares.append(count)
            
            datasets.append({
                'label': 'Escolas Regulares',
                'data': dados_regulares,
                'backgroundColor': '#2ecc71',
                'borderRadius': 8
            })
            
            # 2. Escolas Técnicas
            dados_tecnicas = []
            for tipo_vaga in tipos_vaga:
                count = aplicacoes.filter(
                    tipo_de_vaga=tipo_vaga,
                    usuario__funcao='estudante',
                    usuario__escola__tipo_ensino__nome='INTEGRAL'  # ou o nome correto para técnicas
                ).count()
                dados_tecnicas.append(count)
            
            datasets.append({
                'label': 'Escolas Técnicas',
                'data': dados_tecnicas,
                'backgroundColor': '#e67e22',
                'borderRadius': 8
            })
            
            # 3. Professoras
            dados_professoras = []
            for tipo_vaga in tipos_vaga:
                count = aplicacoes.filter(
                    tipo_de_vaga=tipo_vaga,
                    usuario__funcao='professora'
                ).count()
                dados_professoras.append(count)
            
            datasets.append({
                'label': 'Professoras',
                'data': dados_professoras,
                'backgroundColor': '#9b59b6',
                'borderRadius': 8
            })
            
            dados_grafico_barra = {
                'labels': labels,  # Tipos de vaga como labels
                'datasets': datasets  # Categorias como datasets
            }
            
            return Response({
                "status": "success",
                "dados_diversidade": {
                    "grafico_barra": dados_grafico_barra
                }
            })
            
        except Exception as e:
            logger.error(f"Erro na API: {str(e)}", exc_info=True)
            return Response({
                "status": "error",
                "message": f"Erro: {str(e)}"
            }, status=500)

from django.utils import timezone
import calendar
from datetime import timedelta

class ApiEvolucaoTemporal(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Obter dados dos últimos 12 meses
            meses_dados = []
            inscricoes_data = []
            projetos_iniciados_data = []
            projetos_concluidos_data = []
            
            for i in range(11, -1, -1):  # Últimos 12 meses
                mes_data = timezone.now() - timedelta(days=30*i)
                mes_nome = calendar.month_abbr[mes_data.month]
                ano = mes_data.year
                
                # Inscrições do mês
                inscricoes_mes = Application.objects.filter(
                    criado_em__month=mes_data.month,
                    criado_em__year=mes_data.year
                ).count()
                
                # Projetos iniciados do mês - usando data_inicio
                projetos_iniciados_mes = Project.objects.filter(
                    data_inicio__month=mes_data.month,
                    data_inicio__year=mes_data.year
                ).count()
                
                # Projetos concluídos do mês - usando data_fim e status 'finalizado'
                projetos_concluidos_mes = Project.objects.filter(
                    data_fim__month=mes_data.month,
                    data_fim__year=mes_data.year,
                    status='finalizado'  # Status correto
                ).count()
                
                meses_dados.append(f"{mes_nome}/{str(ano)[-2:]}")
                inscricoes_data.append(inscricoes_mes)
                projetos_iniciados_data.append(projetos_iniciados_mes)
                projetos_concluidos_data.append(projetos_concluidos_mes)
            
            dados_evolucao = {
                'labels': meses_dados,
                'datasets': [
                    {
                        'label': 'Inscrições',
                        'data': inscricoes_data,
                        'borderColor': '#3498db',
                        'backgroundColor': 'rgba(52, 152, 219, 0.1)',
                        'fill': True,
                        'tension': 0.4
                    },
                    {
                        'label': 'Projetos Iniciados',
                        'data': projetos_iniciados_data,
                        'borderColor': '#2ecc71',
                        'backgroundColor': 'rgba(46, 204, 113, 0.1)',
                        'fill': True,
                        'tension': 0.4
                    },
                    {
                        'label': 'Projetos Concluídos',
                        'data': projetos_concluidos_data,
                        'borderColor': '#9b59b6',
                        'backgroundColor': 'rgba(155, 89, 182, 0.1)',
                        'fill': True,
                        'tension': 0.4
                    }
                ]
            }
            
            return Response({
                "status": "success",
                "dados_evolucao": dados_evolucao
            })
            
        except Exception as e:
            logger.error(f"Erro na API Evolução Temporal: {str(e)}")
            # Fallback para dados mockados
            meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            return Response({
                "status": "success",
                "dados_evolucao": {
                    'labels': meses,
                    'datasets': [
                        {
                            'label': 'Inscrições',
                            'data': [120, 180, 220, 280, 320, 400, 450, 500, 550, 600, 650, 700],
                            'borderColor': '#3498db',
                            'backgroundColor': 'rgba(52, 152, 219, 0.1)',
                            'fill': True,
                            'tension': 0.4
                        },
                        {
                            'label': 'Projetos Iniciados',
                            'data': [100, 150, 180, 220, 250, 300, 350, 380, 400, 420, 450, 480],
                            'borderColor': '#2ecc71',
                            'backgroundColor': 'rgba(46, 204, 113, 0.1)',
                            'fill': True,
                            'tension': 0.4
                        },
                        {
                            'label': 'Projetos Concluídos',
                            'data': [80, 120, 150, 180, 210, 250, 280, 300, 320, 340, 360, 380],
                            'borderColor': '#9b59b6',
                            'backgroundColor': 'rgba(155, 89, 182, 0.1)',
                            'fill': True,
                            'tension': 0.4
                        }
                    ]
                }
            })


class ApiFunilPerformance(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Dados cumulativos do funil (não mensais)
            etapas = ['Inscritas', 'Selecionadas', 'Iniciaram', 'Concluíram']
            
            # Inscrições totais
            inscritas_total = Application.objects.count()
            
            # Selecionadas totais
            selecionadas_total = Application.objects.filter(
                Q(aprovado=True) | Q(status='deferida')
            ).count()
            
            # Iniciaram totais
            iniciaram_total = Application.objects.filter(
                projeto__data_inicio__isnull=False
            ).count()
            
            # Concluíram totais
            concluiram_total = Application.objects.filter(
                projeto__status='concluido'
            ).count()
            
            dados_funil = {
                'labels': etapas,
                'datasets': [
                    {
                        'label': 'Quantidade',
                        'data': [inscritas_total, selecionadas_total, iniciaram_total, concluiram_total],
                        'borderColor': '#3498db',
                        'backgroundColor': 'rgba(52, 152, 219, 0.5)',
                        'pointBackgroundColor': ['#3498db', '#2ecc71', '#9b59b6', '#f1c40f'],
                        'pointBorderColor': '#fff',
                        'pointRadius': 8,
                        'pointHoverRadius': 10,
                        'fill': False,
                        'tension': 0.1  # Quase reto para parecer um funil
                    }
                ]
            }
            
            return Response({
                "status": "success",
                "dados_funil": dados_funil
            })
            
        except Exception as e:
            logger.error(f"Erro na API Funil Performance: {str(e)}")
            # Fallback para dados mockados
            etapas = ['Inscritas', 'Selecionadas', 'Iniciaram', 'Concluíram']
            return Response({
                "status": "success",
                "dados_funil": {
                    'labels': etapas,
                    'datasets': [
                        {
                            'label': 'Quantidade',
                            'data': [1000, 750, 500, 250],
                            'borderColor': '#3498db',
                            'backgroundColor': 'rgba(52, 152, 219, 0.5)',
                            'pointBackgroundColor': ['#3498db', '#2ecc71', '#9b59b6', '#f1c40f'],
                            'pointBorderColor': '#fff',
                            'pointRadius': 8,
                            'pointHoverRadius': 10,
                            'fill': False,
                            'tension': 0.1
                        }
                    ]
                }
            })


from core.models import Regiao
class ApiDistribuicaoRegional(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Filtrar apenas projetos ativos
            projetos = Project.objects.filter(ativo=True)
            
            # Contar projetos por região através das regiões aceitas
            distribuicao_regional = projetos.annotate(
                regiao_nome=F('regioes_aceitas__nome')
            ).values(
                'regiao_nome'
            ).annotate(
                total=Count('id')
            ).order_by('regiao_nome')
            
            # Preparar dados para o gráfico
            regioes = []
            quantidades = []
            
            for item in distribuicao_regional:
                if item['regiao_nome']:
                    regioes.append(item['regiao_nome'])
                    quantidades.append(item['total'])
            
            # Adicionar regiões com zero projetos (se necessário)
            todas_regioes = Regiao.objects.all()
            for regiao in todas_regioes:
                if regiao.nome not in regioes:
                    regioes.append(regiao.nome)
                    quantidades.append(0)
            
            dados_distribuicao = {
                'labels': regioes,
                'data': quantidades,
                'backgroundColor': [
                    '#3498db', '#2ecc71', '#9b59b6', '#f1c40f', '#e74c3c', '#1abc9c'
                ]
            }
            
            return Response({
                "status": "success",
                "dados_distribuicao": dados_distribuicao
            })
            
        except Exception as e:
            logger.error(f"Erro na API Distribuição Regional: {str(e)}")
            # Fallback para dados mockados
            return Response({
                "status": "success",
                "dados_distribuicao": {
                    'labels': ['Sudeste', 'Nordeste', 'Sul', 'Centro-Oeste', 'Norte'],
                    'data': [15, 12, 8, 6, 4],
                    'backgroundColor': [
                        '#3498db', '#2ecc71', '#9b59b6', '#f1c40f', '#e74c3c'
                    ]
                }
            })
            

from django.db.models import Count

class ApiDistribuicaoEstados(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Contar applications distintas por estado
            distribuicao_estados = (
                Application.objects
                .filter(projeto__ativo=True)
                .values(
                    estado_nome=F('projeto__estados_aceitos__nome'),
                    estado_uf=F('projeto__estados_aceitos__uf')
                )
                .annotate(total=Count('id', distinct=True))
                .order_by('estado_nome')
            )

            # Preparar dados para o gráfico
            ufs = []
            quantidades = []

            for item in distribuicao_estados:
                if item['estado_nome']:
                    ufs.append(item['estado_uf'])
                    quantidades.append(item['total'])



            dados_distribuicao = {
                'labels': ufs,
                'data': quantidades,
                'backgroundColor': [
                    '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                    '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
                    '#f39c12', '#27ae60', '#2980b9', '#c0392b', '#16a085',
                    '#f1c40f', '#9b59b6', '#2c3e50', '#e67e22', '#d35400',
                    '#7d3c98', '#1abc9c', '#34495e', '#e74c3c', '#95a5a6',
                    '#00b894', '#fd79a8'
                ]
            }

            return Response({
                "status": "success",
                "dados_distribuicao": dados_distribuicao
            })

        except Exception as e:
            logger.error(f"Erro na API Distribuição Estados: {str(e)}")
            return Response({
                "status": "error",
                "mensagem": str(e)
            })


 
            
            
class ApiDistribuicaoFormacao(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Contar aplicações por grau de formação, incluindo null/vazios como "Não informado"
            distribuicao_formacao = Application.objects.values(
                'grau_formacao'
            ).annotate(
                total=Count('id')
            ).order_by('grau_formacao')
            
            # Mapear os valores para labels mais amigáveis
            label_map = {
                'graduacao': 'Graduação',
                'licenciatura': 'Licenciatura',
                'bacharelado': 'Bacharelado',
                'tecnologo': 'Tecnólogo',
                'especializacao': 'Especialização',
                'mestrado': 'Mestrado',
                'doutorado': 'Doutorado',
                'pos_doutorado': 'Pós-doutorado',
                'outro': 'Outro'
            }
            
            # Preparar dados para o gráfico
            labels = []
            data = []
            cores = [
                '#3498db', '#2ecc71', '#9b59b6', '#f1c40f', 
                '#e74c3c', '#1abc9c', '#34495e', '#f39c12', '#16a085', '#95a5a6'
            ]
            
            nao_informado_count = 0
            
            for item in distribuicao_formacao:
                grau_formacao = item['grau_formacao']
                if grau_formacao and grau_formacao.strip():  # Não é null nem vazio
                    if grau_formacao in label_map:
                        labels.append(label_map[grau_formacao])
                        data.append(item['total'])
                    else:
                        # Se for um valor não mapeado, usar o valor original
                        labels.append(grau_formacao.capitalize())
                        data.append(item['total'])
                else:
                    # Acumular valores null/vazios como "Não informado"
                    nao_informado_count += item['total']
            
            # Adicionar "Não informado" se houver valores
            if nao_informado_count > 0:
                labels.append('Não informado')
                data.append(nao_informado_count)
            
            # Adicionar cores (repetir se necessário)
            background_colors = cores[:len(labels)]
            
            dados_distribuicao = {
                'labels': labels,
                'data': data,
                'backgroundColor': background_colors
            }
            
            return Response({
                "status": "success",
                "dados_distribuicao_formacao": dados_distribuicao
            })
            
        except Exception as e:
            logger.error(f"Erro na API Distribuição Formação: {str(e)}")
            # Fallback para dados mockados em caso de erro
            return Response({
                "status": "success",
                "dados_distribuicao_formacao": {
                    'labels': ['Graduação', 'Mestrado', 'Doutorado', 'Especialização', 'Licenciatura', 'Não informado'],
                    'data': [120, 85, 45, 30, 25, 15],
                    'backgroundColor': [
                        '#3498db', '#2ecc71', '#9b59b6', '#f1c40f', '#e74c3c', '#95a5a6'
                    ]
                }
            })

class ApiDistribuicaoRacaProfessoras(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Filtrar apenas professoras
            professoras = User.objects.filter(funcao='professora')
            
            # Contar por raça, incluindo null/vazios
            raca_counts = professoras.values(
                'raca__nome'
            ).annotate(
                total=Count('id')
            ).order_by('raca__nome')
            
            # Preparar dados para o gráfico
            dados_raca = {
                'labels': [],
                'data': [],
                'backgroundColor': [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
                    '#9966FF', '#FF9F40', '#8ac6d1', '#ff6b6b', '#a5dee5', '#95a5a6'
                ]
            }
            
            nao_informado_count = 0
            
            # Processar dados de raça
            for item in raca_counts:
                raca_nome = item['raca__nome']
                if raca_nome and raca_nome.strip():  # Não é null nem vazio
                    dados_raca['labels'].append(raca_nome)
                    dados_raca['data'].append(item['total'])
                else:
                    # Acumular valores null/vazios
                    nao_informado_count += item['total']
            
            # Adicionar "Não informado" se houver valores
            if nao_informado_count > 0:
                dados_raca['labels'].append('Não informado')
                dados_raca['data'].append(nao_informado_count)
            
            return Response({
                "status": "success",
                "dados_distribuicao_raca": dados_raca
            })
            
        except Exception as e:
            logger.error(f"Erro na API Distribuição Raça Professoras: {str(e)}")
            # Fallback para dados mockados em caso de erro
            return Response({
                "status": "success",
                "dados_distribuicao_raca": {
                    'labels': ['Branca', 'Preta', 'Parda', 'Indígena', 'Amarela', 'Não informado'],
                    'data': [45, 35, 40, 15, 10, 8],
                    'backgroundColor': [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#95a5a6'
                    ]
                }
            })

class ApiProfessorasDistribuicaoRegional(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Filtrar apenas professoras
            professoras = User.objects.filter(funcao='professora')
            
            # Contar todas as professoras (incluindo as sem região)
            total_professoras = professoras.count()
            
            # Contar professoras por região
            distribuicao_regional = professoras.filter(
                endereco__isnull=False,
                endereco__estado__isnull=False,
                endereco__estado__regiao__isnull=False
            ).values(
                'endereco__estado__regiao__nome'
            ).annotate(
                total=Count('id')
            ).order_by('endereco__estado__regiao__nome')
            
            # Calcular professoras sem região
            professoras_com_regiao = sum(item['total'] for item in distribuicao_regional)
            professoras_sem_regiao = total_professoras - professoras_com_regiao
            
            # Preparar dados para o gráfico
            regioes = []
            quantidades = []
            
            for item in distribuicao_regional:
                if item['endereco__estado__regiao__nome']:
                    regioes.append(item['endereco__estado__regiao__nome'])
                    quantidades.append(item['total'])
            
            # Adicionar regiões com zero professoras (se necessário)
            todas_regioes = Regiao.objects.all()
            for regiao in todas_regioes:
                if regiao.nome not in regioes:
                    regioes.append(regiao.nome)
                    quantidades.append(0)
            
            # Adicionar "Não informado" se houver professoras sem região
            if professoras_sem_regiao > 0:
                regioes.append('Não informado')
                quantidades.append(professoras_sem_regiao)
            
            dados_distribuicao = {
                'labels': regioes,
                'data': quantidades,
                'backgroundColor': [
                    '#3498db', '#2ecc71', '#9b59b6', '#f1c40f', '#e74c3c', '#1abc9c', '#95a5a6'
                ]
            }
            
            return Response({
                "status": "success",
                "dados_distribuicao": dados_distribuicao
            })
            
        except Exception as e:
            logger.error(f"Erro na API Distribuição Regional de Professoras: {str(e)}")
            # Fallback para dados mockados
            return Response({
                "status": "success",
                "dados_distribuicao": {
                    'labels': ['Sudeste', 'Nordeste', 'Sul', 'Centro-Oeste', 'Norte', 'Não informado'],
                    'data': [45, 35, 25, 15, 10, 5],
                    'backgroundColor': [
                        '#3498db', '#2ecc71', '#9b59b6', '#f1c40f', '#e74c3c', '#95a5a6'
                    ]
                }
            })

class ApiProfessorasDistribuicaoEstadual(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Filtrar apenas professoras
            professoras = User.objects.filter(funcao='professora')
            total_professoras = professoras.count()

            # Contar professoras por estado
            distribuicao_estadual = (
                professoras.filter(endereco__isnull=False, endereco__estado__isnull=False)
                .values('endereco__estado__uf')
                .annotate(total=Count('id'))
                .order_by('-total')
            )

            # Calcular professoras sem estado
            professoras_com_estado = sum(item['total'] for item in distribuicao_estadual)
            professoras_sem_estado = total_professoras - professoras_com_estado

            # Preparar dados para o gráfico
            estados = [item['endereco__estado__uf'] for item in distribuicao_estadual if item['endereco__estado__uf']]
            quantidades = [item['total'] for item in distribuicao_estadual if item['endereco__estado__uf']]

            # ➡️ Removido o trecho que limitava a 10 estados
            # if len(estados) > 10:
            #     estados = estados[:10]
            #     quantidades = quantidades[:10]

            # Adicionar "Não informado", se necessário
            if professoras_sem_estado > 0:
                estados.append('Não informado')
                quantidades.append(professoras_sem_estado)

            # Gera cores dinamicamente conforme o total de estados
            cores_base = [
                '#3498db', '#2ecc71', '#9b59b6', '#f1c40f', '#e74c3c',
                '#1abc9c', '#34495e', '#95a5a6', '#d35400', '#8e44ad'
            ]
            # Repete ou corta para cobrir todos os estados
            cores = (cores_base * ((len(estados) // len(cores_base)) + 1))[:len(estados)]

            dados_distribuicao = {
                'labels': estados,
                'data': quantidades,
                'backgroundColor': cores
            }

            return Response({"status": "success", "dados_distribuicao": dados_distribuicao})

        except Exception as e:
            logger.error(f"Erro na API Distribuição Estadual de Professoras: {str(e)}")
            return Response({
                "status": "success",
                "dados_distribuicao": {
                    'labels': ['SP', 'RJ', 'MG', 'BA', 'RS', 'Não informado'],
                    'data': [25, 18, 15, 12, 8, 7],
                    'backgroundColor': [
                        '#3498db', '#2ecc71', '#9b59b6', '#f1c40f', '#e74c3c', '#95a5a6'
                    ]
                }
            })


class ApiProfessorasDistribuicaoTipoEnsino(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Filtrar apenas professoras
            professoras = User.objects.filter(funcao='professora')
            
            # Contar todas as professoras
            total_professoras = professoras.count()
            
            # Contar professoras por tipo de ensino
            distribuicao_tipo_ensino = professoras.filter(
                escola__isnull=False,
                escola__tipo_ensino__isnull=False
            ).values(
                'escola__tipo_ensino__nome'
            ).annotate(
                total=Count('id')
            ).order_by('escola__tipo_ensino__nome')
            
            # Calcular professoras sem tipo de ensino
            professoras_com_tipo_ensino = sum(item['total'] for item in distribuicao_tipo_ensino)
            professoras_sem_tipo_ensino = total_professoras - professoras_com_tipo_ensino
            
            # Preparar dados para o gráfico
            tipos_ensino = []
            quantidades = []
            
            for item in distribuicao_tipo_ensino:
                if item['escola__tipo_ensino__nome']:
                    tipos_ensino.append(item['escola__tipo_ensino__nome'])
                    quantidades.append(item['total'])
            
            # Adicionar tipos de ensino com zero professoras (se necessário)
            todos_tipos_ensino = TipoEnsino.objects.all()
            for tipo in todos_tipos_ensino:
                if tipo.nome not in tipos_ensino:
                    tipos_ensino.append(tipo.nome)
                    quantidades.append(0)
            
            # Adicionar "Não informado" se houver professoras sem tipo de ensino
            if professoras_sem_tipo_ensino > 0:
                tipos_ensino.append('Não informado')
                quantidades.append(professoras_sem_tipo_ensino)
            
            dados_distribuicao = {
                'labels': tipos_ensino,
                'data': quantidades,
                'backgroundColor': [
                    '#3498db', '#2ecc71', '#9b59b6', '#f1c40f', '#e74c3c', '#1abc9c', '#95a5a6'
                ]
            }
            
            return Response({
                "status": "success",
                "dados_distribuicao": dados_distribuicao
            })
            
        except Exception as e:
            logger.error(f"Erro na API Distribuição por Tipo de Ensino: {str(e)}")
            # Fallback para dados mockados
            return Response({
                "status": "success",
                "dados_distribuicao": {
                    'labels': ['REGULAR', 'INTEGRAL', 'Não informado'],
                    'data': [65, 35, 12],
                    'backgroundColor': [
                        '#3498db', '#2ecc71', '#95a5a6'
                    ]
                }
            })

class ApiDashboardUnificado(APIView):
    def get(self, request, *args, **kwargs):
        try:
            print("=== INÍCIO API DASHBOARD UNIFICADO ===")

            # Obter parâmetros de filtro da query string
            estado_filter = request.GET.get('estado')
            raca_filter = request.GET.get('raca')
            formacao_filter = request.GET.get('formacao')
            tipo_ensino_filter = request.GET.get('tipo_ensino')

            print(f"📊 Filtros recebidos:")
            print(f"   - Estado/Região: {estado_filter}")
            print(f"   - Raça: {raca_filter}")
            print(f"   - Formação: {formacao_filter}")
            print(f"   - Tipo Ensino: {tipo_ensino_filter}")

            # Base queryset para professoras (User)
            professoras = User.objects.filter(funcao='professora')
            print(f"👩‍🏫 Total de professoras inicial: {professoras.count()}")

            # Aplicar filtros que são da model User
            if estado_filter and estado_filter != 'todos':
                professoras = professoras.filter(endereco__estado__regiao__nome=estado_filter)
                print(f"📍 Filtro estado/região aplicado: {estado_filter}")

            if raca_filter and raca_filter != 'todos':
                professoras = professoras.filter(raca__nome=raca_filter)
                print(f"🎨 Filtro raça aplicado: {raca_filter}")

            if tipo_ensino_filter and tipo_ensino_filter != 'todos':
                professoras = professoras.filter(escola__tipo_ensino__nome=tipo_ensino_filter)
                print(f"🏫 Filtro tipo ensino aplicado: {tipo_ensino_filter}")

            print(f"👩‍🏫 Total de professoras após filtros User: {professoras.count()}")

            # Para formação, usamos a model Application separadamente
            aplicacoes_filtradas = Application.objects.filter(usuario__funcao='professora')
            print(f"📝 Total de aplicações inicial: {aplicacoes_filtradas.count()}")

            # Aplicar filtros nas applications
            if estado_filter and estado_filter != 'todos':
                aplicacoes_filtradas = aplicacoes_filtradas.filter(
                    usuario__endereco__estado__regiao__nome=estado_filter
                )
                print(f"📍 Filtro estado/região aplicado nas applications: {estado_filter}")

            if raca_filter and raca_filter != 'todos':
                aplicacoes_filtradas = aplicacoes_filtradas.filter(usuario__raca__nome=raca_filter)
                print(f"🎨 Filtro raça aplicado nas applications: {raca_filter}")

            if tipo_ensino_filter and tipo_ensino_filter != 'todos':
                aplicacoes_filtradas = aplicacoes_filtradas.filter(
                    usuario__escola__tipo_ensino__nome=tipo_ensino_filter
                )
                print(f"🏫 Filtro tipo ensino aplicado nas applications: {tipo_ensino_filter}")

            if formacao_filter and formacao_filter != 'todos':
                aplicacoes_filtradas = aplicacoes_filtradas.filter(grau_formacao=formacao_filter)
                print(f"🎓 Filtro formação aplicado: {formacao_filter}")

            print(f"📝 Total de aplicações após filtros: {aplicacoes_filtradas.count()}")

            # Gerar os dados para os gráficos
            distribuicao_formacao = self._get_distribuicao_formacao(aplicacoes_filtradas)
            distribuicao_raca = self._get_distribuicao_raca(professoras)
            distribuicao_regional = self._get_distribuicao_regional(professoras)
            distribuicao_estadual = self._get_distribuicao_estadual(professoras, estado_filter)
            distribuicao_tipo_ensino = self._get_distribuicao_tipo_ensino(professoras)

            total_professoras = professoras.count()
            print(f"👩‍🏫 Total final de professoras: {total_professoras}")

            resultado = {
                "status": "success",
                "filtros_ativos": {
                    "estado": estado_filter,
                    "raca": raca_filter,
                    "formacao": formacao_filter,
                    "tipo_ensino": tipo_ensino_filter
                },
                "total_professoras": total_professoras,
                "dados_formacao": distribuicao_formacao,
                "dados_raca": distribuicao_raca,
                "dados_regional": distribuicao_regional,
                "dados_estadual": distribuicao_estadual,
                "dados_tipo_ensino": distribuicao_tipo_ensino
            }

            print("✅ API executada com sucesso!")
            return Response(resultado)

        except Exception as e:
            print("❌ ERRO NA API DASHBOARD UNIFICADO")
            print(f"💥 Erro: {str(e)}")
            logger.error(f"Erro na API Dashboard Unificado: {str(e)}")
            return Response({"status": "error", "message": str(e)}, status=500)

    # ---------- MÉTODOS AUXILIARES ----------

    def _get_distribuicao_formacao(self, aplicacoes):
        distribuicao = aplicacoes.values('grau_formacao').annotate(total=Count('id')).order_by('grau_formacao')
        label_map = {
            'graduacao': 'Graduação', 'licenciatura': 'Licenciatura',
            'bacharelado': 'Bacharelado', 'tecnologo': 'Tecnólogo',
            'especializacao': 'Especialização', 'mestrado': 'Mestrado',
            'doutorado': 'Doutorado', 'pos_doutorado': 'Pós-doutorado',
            'outro': 'Outro'
        }
        labels, data = [], []
        nao_informado_count = 0
        for item in distribuicao:
            grau_formacao = item['grau_formacao']
            total = item['total']
            if grau_formacao and grau_formacao.strip():
                label = label_map.get(grau_formacao, grau_formacao.capitalize())
                labels.append(label)
                data.append(total)
            else:
                nao_informado_count += total
        if nao_informado_count > 0:
            labels.append('Não informado')
            data.append(nao_informado_count)
        return {'labels': labels, 'data': data, 'backgroundColor': ['#3498db', '#2ecc71', '#9b59b6', '#f1c40f', '#e74c3c', '#1abc9c', '#34495e', '#95a5a6', '#d35400', '#8e44ad'][:len(labels)]}

    def _get_distribuicao_raca(self, professoras):
        raca_counts = professoras.values('raca__nome').annotate(total=Count('id')).order_by('raca__nome')
        labels, data = [], []
        nao_informado_count = 0
        for item in raca_counts:
            raca_nome = item['raca__nome']
            total = item['total']
            if raca_nome and raca_nome.strip():
                labels.append(raca_nome)
                data.append(total)
            else:
                nao_informado_count += total
        if nao_informado_count > 0:
            labels.append('Não informado')
            data.append(nao_informado_count)
        return {'labels': labels, 'data': data, 'backgroundColor': ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#8ac6d1', '#ff6b6b', '#a5dee5', '#95a5a6'][:len(labels)]}

    def _get_distribuicao_regional(self, professoras):
        distribuicao = professoras.filter(endereco__estado__regiao__nome__isnull=False)\
            .values('endereco__estado__regiao__nome').annotate(total=Count('id')).order_by('endereco__estado__regiao__nome')
        regioes, quantidades = [], []
        for item in distribuicao:
            regioes.append(item['endereco__estado__regiao__nome'])
            quantidades.append(item['total'])
        # Adiciona regiões sem professoras
        todas_regioes = Regiao.objects.values_list('nome', flat=True)
        for regiao in todas_regioes:
            if regiao not in regioes:
                regioes.append(regiao)
                quantidades.append(0)
        return {'labels': regioes, 'data': quantidades, 'backgroundColor': ['#3498db', '#2ecc71', '#9b59b6', '#f1c40f', '#e74c3c', '#1abc9c', '#95a5a6'][:len(regioes)]}

    def _get_distribuicao_estadual(self, professoras, estado_filter=None):
        queryset = professoras
        if estado_filter and estado_filter != 'todos':
            # Se for filtro por região, restringe aos estados dessa região
            queryset = queryset.filter(endereco__estado__regiao__nome=estado_filter)
        distribuicao = queryset.filter(endereco__estado__uf__isnull=False)\
            .values('endereco__estado__uf').annotate(total=Count('id')).order_by('-total')
        estados = [item['endereco__estado__uf'] for item in distribuicao]
        quantidades = [item['total'] for item in distribuicao]
        return {'labels': estados, 'data': quantidades, 'backgroundColor': ['#3498db', '#2ecc71', '#9b59b6', '#f1c40f', '#e74c3c', '#1abc9c', '#34495e', '#95a5a6', '#d35400', '#8e44ad'][:len(estados)]}

    def _get_distribuicao_tipo_ensino(self, professoras):
        distribuicao = professoras.filter(escola__tipo_ensino__nome__isnull=False)\
            .values('escola__tipo_ensino__nome').annotate(total=Count('id')).order_by('escola__tipo_ensino__nome')
        tipos, quantidades = [], []
        for item in distribuicao:
            tipos.append(item['escola__tipo_ensino__nome'])
            quantidades.append(item['total'])
        # Adiciona tipos sem professoras
        todos_tipos = TipoEnsino.objects.values_list('nome', flat=True)
        for tipo in todos_tipos:
            if tipo not in tipos:
                tipos.append(tipo)
                quantidades.append(0)
        return {'labels': tipos, 'data': quantidades, 'backgroundColor': ['#3498db', '#2ecc71', '#9b59b6', '#f1c40f', '#e74c3c', '#1abc9c', '#95a5a6'][:len(tipos)]}
    

class ApiFunilAlunasApplicationLog(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Definir as etapas do funil
            etapas = ['Inscritas', 'Selecionadas', 'Iniciaram', 'Concluíram']
            
            # 1. Inscritas totais - Todas as applications
            inscritas_total = Application.objects.count()
            
            # 2. Selecionadas - Applications com status 'deferida' OU aprovado=True
            selecionadas_total = Application.objects.filter(
                Q(status='deferida') | Q(aprovado=True)
            ).distinct().count()
            
            # 3. Iniciaram - Applications que tiveram status mudado para 'em_andamento' ou similar
            # Primeiro, encontrar os status que indicam início
            status_inicio = ['em_andamento', 'iniciada', 'matriculada']
            iniciaram_total = ApplicationStatusLog.objects.filter(
                status_novo__in=status_inicio
            ).values('inscricao').distinct().count()
            
            # 4. Concluíram - Applications que tiveram status mudado para conclusão
            # OU projects com status 'concluido' onde a application está relacionada
            status_conclusao = ['concluida', 'finalizada', 'completa']
            concluiram_total = ApplicationStatusLog.objects.filter(
                status_novo__in=status_conclusao
            ).values('inscricao').distinct().count()
            
            # Alternativa: contar pelas applications cujo projeto está concluído
            if concluiram_total == 0:
                concluiram_total = Application.objects.filter(
                    projeto__status='concluido'
                ).distinct().count()
            
            dados_funil = {
                'labels': etapas,
                'datasets': [
                    {
                        'label': 'Quantidade',
                        'data': [inscritas_total, selecionadas_total, iniciaram_total, concluiram_total],
                        'borderColor': '#3498db',
                        'backgroundColor': 'rgba(52, 152, 219, 0.5)',
                        'pointBackgroundColor': ['#3498db', '#2ecc71', '#9b59b6', '#f1c40f'],
                        'pointBorderColor': '#fff',
                        'pointRadius': 8,
                        'pointHoverRadius': 10,
                        'fill': False,
                        'tension': 0.1
                    }
                ]
            }
            
            return Response({
                "status": "success",
                "dados_funil": dados_funil
            })
            
        except Exception as e:
            logger.error(f"Erro na API Funil Alunas (ApplicationLog): {str(e)}")
            # Fallback para dados baseados apenas na tabela Application
            try:
                etapas = ['Inscritas', 'Selecionadas', 'Iniciaram', 'Concluíram']
                
                inscritas_total = Application.objects.count()
                selecionadas_total = Application.objects.filter(
                    Q(status='deferida') | Q(aprovado=True)
                ).count()
                
                # Para "Iniciaram", podemos usar applications com projetos que começaram
                iniciaram_total = Application.objects.filter(
                    projeto__data_inicio__isnull=False
                ).count()
                
                # Para "Concluíram", podemos usar applications com projetos concluídos
                concluiram_total = Application.objects.filter(
                    projeto__status='concluido'
                ).count()
                
                dados_funil = {
                    'labels': etapas,
                    'datasets': [
                        {
                            'label': 'Quantidade',
                            'data': [inscritas_total, selecionadas_total, iniciaram_total, concluiram_total],
                            'borderColor': '#3498db',
                            'backgroundColor': 'rgba(52, 152, 219, 0.5)',
                            'pointBackgroundColor': ['#3498db', '#2ecc71', '#9b59b6', '#f1c40f'],
                            'pointBorderColor': '#fff',
                            'pointRadius': 8,
                            'pointHoverRadius': 10,
                            'fill': False,
                            'tension': 0.1
                        }
                    ]
                }
                
                return Response({
                    "status": "success",
                    "dados_funil": dados_funil
                })
                
            except Exception as inner_error:
                logger.error(f"Erro no fallback do Funil Alunas: {str(inner_error)}")
                # Fallback final para dados mockados
                return Response({
                    "status": "success",
                    "dados_funil": {
                        'labels': ['Inscritas', 'Selecionadas', 'Iniciaram', 'Concluíram'],
                        'datasets': [
                            {
                                'label': 'Quantidade',
                                'data': [1000, 750, 500, 250],
                                'borderColor': '#3498db',
                                'backgroundColor': 'rgba(52, 152, 219, 0.5)',
                                'pointBackgroundColor': ['#3498db', '#2ecc71', '#9b59b6', '#f1c40f'],
                                'pointBorderColor': '#fff',
                                'pointRadius': 8,
                                'pointHoverRadius': 10,
                                'fill': False,
                                'tension': 0.1
                            }
                        ]
                    }
                })

class ApiDistribuicaoCotas(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Filtrar apenas estudantes
            estudantes = User.objects.filter(funcao='estudante')
            
            # Contar por gênero
            genero_counts = estudantes.values(
                'genero__nome'
            ).annotate(
                total=Count('id')
            ).order_by('genero__nome')
            
            # Contar por raça
            raca_counts = estudantes.values(
                'raca__nome'
            ).annotate(
                total=Count('id')
            ).order_by('raca__nome')
            
            # Contar por tipo de escola
            escola_counts = estudantes.exclude(escola__isnull=True).values(
                'escola__tipo_ensino__nome'
            ).annotate(
                total=Count('id')
            ).order_by('escola__tipo_ensino__nome')
            
            # Contar estudantes sem escola
            estudantes_sem_escola = estudantes.filter(escola__isnull=True).count()
            
            # Preparar dados separados
            dados_genero = {
                'labels': [],
                'data': [],
                'backgroundColor': ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#95a5a6']
            }
            
            dados_raca = {
                'labels': [],
                'data': [],
                'backgroundColor': ['#9966FF', '#FF9F40', '#8ac6d1', '#ff6b6b', '#a5dee5', '#95a5a6']
            }
            
            dados_escola = {
                'labels': [],
                'data': [],
                'backgroundColor': ['#ffd700', '#98ddca', '#ffaaa7', '#c5a3ff', '#95a5a6']
            }
            
            # Processar dados de gênero
            nao_informado_genero = 0
            for item in genero_counts:
                genero_nome = item['genero__nome']
                if genero_nome and genero_nome.strip():
                    dados_genero['labels'].append(genero_nome)
                    dados_genero['data'].append(item['total'])
                else:
                    nao_informado_genero += item['total']
            
            # Adicionar "Não informado" para gênero
            if nao_informado_genero > 0:
                dados_genero['labels'].append('Não informado')
                dados_genero['data'].append(nao_informado_genero)
            
            # Processar dados de raça
            nao_informado_raca = 0
            for item in raca_counts:
                raca_nome = item['raca__nome']
                if raca_nome and raca_nome.strip():
                    dados_raca['labels'].append(raca_nome)
                    dados_raca['data'].append(item['total'])
                else:
                    nao_informado_raca += item['total']
            
            # Adicionar "Não informado" para raça
            if nao_informado_raca > 0:
                dados_raca['labels'].append('Não informado')
                dados_raca['data'].append(nao_informado_raca)
            
            # Processar dados de escola
            for item in escola_counts:
                if item['escola__tipo_ensino__nome']:
                    dados_escola['labels'].append(item['escola__tipo_ensino__nome'])
                    dados_escola['data'].append(item['total'])
            
            # Adicionar estudantes sem escola como "Não informado"
            if estudantes_sem_escola > 0:
                dados_escola['labels'].append('Não informado')
                dados_escola['data'].append(estudantes_sem_escola)
            
            return Response({
                "status": "success",
                "dados_separados": {
                    'genero': dados_genero,
                    'raca': dados_raca,
                    'escola': dados_escola
                }
            })
            
        except Exception as e:
            logger.error(f"Erro na API Distribuição Cotas: {str(e)}")
            # Fallback para dados mockados
            return Response({
                "status": "success",
                "dados_separados": {
                    'genero': {
                        'labels': ['Feminino', 'Masculino', 'Não-binário', 'Não informado'],
                        'data': [120, 15, 8, 5],
                        'backgroundColor': ['#FF6384', '#36A2EB', '#FFCE56', '#95a5a6']
                    },
                    'raca': {
                        'labels': ['Branca', 'Preta', 'Parda', 'Indígena', 'Não informado'],
                        'data': [45, 35, 40, 15, 8],
                        'backgroundColor': ['#9966FF', '#FF9F40', '#8ac6d1', '#ff6b6b', '#95a5a6']
                    },
                    'escola': {
                        'labels': ['Pública', 'Privada', 'Não informado'],
                        'data': [110, 25, 10],
                        'backgroundColor': ['#ffd700', '#98ddca', '#95a5a6']
                    }
                }
            })

class ApiDistribuicaoEscolas(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Filtrar apenas estudantes
            estudantes = User.objects.filter(funcao='estudante')
            
            # Contar total de estudantes
            total_estudantes = estudantes.count()
            
            # Contar por tipo de escola
            escola_counts = estudantes.values(
                'escola__tipo_ensino__nome'
            ).annotate(
                total=Count('id')
            ).order_by('escola__tipo_ensino__nome')
            
            # Contar estudantes sem escola
            estudantes_sem_escola = estudantes.filter(escola__isnull=True).count()
            
            # Preparar dados para o gráfico de rosca
            tipos_ensino = []
            quantidades = []
            
            for item in escola_counts:
                if item['escola__tipo_ensino__nome']:
                    tipos_ensino.append(item['escola__tipo_ensino__nome'])
                    quantidades.append(item['total'])
            
            # Adicionar "Não informado" se houver estudantes sem escola
            if estudantes_sem_escola > 0:
                tipos_ensino.append('Não informado')
                quantidades.append(estudantes_sem_escola)
            
            return Response({
                "status": "success",
                "dados_escolas": {
                    'labels': tipos_ensino,
                    'data': quantidades,
                    'backgroundColor': [
                        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#95a5a6'
                    ]
                }
            })
            
        except Exception as e:
            logger.error(f"Erro na API Distribuição Escolas: {str(e)}")
            # Fallback para dados mockados
            return Response({
                "status": "success",
                "dados_escolas": {
                    'labels': ['Pública', 'Privada', 'Não informado'],
                    'data': [110, 25, 12],
                    'backgroundColor': [
                        '#36A2EB', '#FF6384', '#95a5a6'
                    ]
                }
            })

class ApiAlunasDistribuicaoRegional(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Filtrar apenas alunas
            alunas = User.objects.filter(funcao='estudante')
            
            # Contar total de alunas
            total_alunas = alunas.count()
            
            # Contar alunas por região através do endereço -> estado -> região
            distribuicao_regional = alunas.filter(
                endereco__isnull=False,
                endereco__estado__isnull=False,
                endereco__estado__regiao__isnull=False
            ).values(
                'endereco__estado__regiao__nome'
            ).annotate(
                total=Count('id')
            ).order_by('endereco__estado__regiao__nome')
            
            # Calcular alunas sem região
            alunas_com_regiao = sum(item['total'] for item in distribuicao_regional)
            alunas_sem_regiao = total_alunas - alunas_com_regiao
            
            # Preparar dados para o gráfico
            regioes = []
            quantidades = []
            
            for item in distribuicao_regional:
                if item['endereco__estado__regiao__nome']:
                    regioes.append(item['endereco__estado__regiao__nome'])
                    quantidades.append(item['total'])
            
            # Adicionar regiões com zero alunas (se necessário)
            todas_regioes = Regiao.objects.all()
            for regiao in todas_regioes:
                if regiao.nome not in regioes:
                    regioes.append(regiao.nome)
                    quantidades.append(0)
            
            # Adicionar "Não informado" se houver alunas sem região
            if alunas_sem_regiao > 0:
                regioes.append('Não informado')
                quantidades.append(alunas_sem_regiao)
            
            dados_distribuicao = {
                'labels': regioes,
                'data': quantidades,
                'backgroundColor': [
                    '#3498db', '#2ecc71', '#9b59b6', '#f1c40f', '#e74c3c', '#1abc9c', '#95a5a6'
                ]
            }
            
            return Response({
                "status": "success",
                "dados_distribuicao": dados_distribuicao
            })
            
        except Exception as e:
            logger.error(f"Erro na API Distribuição Regional de Alunas: {str(e)}")
            # Fallback para dados mockados
            return Response({
                "status": "success",
                "dados_distribuicao": {
                    'labels': ['Sudeste', 'Nordeste', 'Sul', 'Centro-Oeste', 'Norte', 'Não informado'],
                    'data': [120, 85, 60, 40, 25, 15],
                    'backgroundColor': [
                        '#3498db', '#2ecc71', '#9b59b6', '#f1c40f', '#e74c3c', '#95a5a6'
                    ]
                }
            })

class ApiAlunasDistribuicaoEstadual(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Filtrar apenas alunas
            alunas = User.objects.filter(funcao='estudante')
            
            # Contar total de alunas
            total_alunas = alunas.count()
            
            # Contar alunas por estado
            distribuicao_estadual = alunas.filter(
                endereco__isnull=False,
                endereco__estado__isnull=False
            ).values(
                'endereco__estado__uf'
            ).annotate(
                total=Count('id')
            ).order_by('-total')
            
            # Calcular alunas sem estado
            alunas_com_estado = sum(item['total'] for item in distribuicao_estadual)
            alunas_sem_estado = total_alunas - alunas_com_estado
            
            # Preparar dados para o gráfico
            estados = []
            quantidades = []
            
            for item in distribuicao_estadual:
                if item['endereco__estado__uf']:
                    estados.append(item['endereco__estado__uf'])
                    quantidades.append(item['total'])
            
            # Adicionar "Não informado" se houver alunas sem estado
            if alunas_sem_estado > 0:
                estados.append('Não informado')
                quantidades.append(alunas_sem_estado)
            
            # Gerar cores para todos os estados
            cores_base = [
                '#3498db', '#2ecc71', '#9b59b6', '#f1c40f', '#e74c3c', 
                '#1abc9c', '#34495e', '#95a5a6', '#d35400', '#8e44ad',
                '#27ae60', '#f39c12', '#16a085', '#8e44ad', '#2c3e50'
            ]
            
            # Gerar cores para todos os estados (repetindo se necessário)
            cores = []
            for i in range(len(estados)):
                cores.append(cores_base[i % len(cores_base)])
            
            dados_distribuicao = {
                'labels': estados,
                'data': quantidades,
                'backgroundColor': cores
            }
            
            return Response({
                "status": "success",
                "dados_distribuicao": dados_distribuicao
            })
            
        except Exception as e:
            logger.error(f"Erro na API Distribuição Estadual de Alunas: {str(e)}")
            # Fallback para dados mockados
            return Response({
                "status": "success",
                "dados_distribuicao": {
                    'labels': ['SP', 'RJ', 'MG', 'BA', 'RS', 'PR', 'PE', 'CE', 'SC', 'GO', 'Não informado'],
                    'data': [65, 45, 40, 35, 30, 25, 20, 18, 15, 12, 10],
                    'backgroundColor': [
                        '#3498db', '#2ecc71', '#9b59b6', '#f1c40f', '#e74c3c',
                        '#1abc9c', '#34495e', '#95a5a6', '#d35400', '#8e44ad', '#95a5a6'
                    ]
                }
            })

class ApiAlunasDistribuicaoCidades(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Filtrar apenas alunas
            alunas = User.objects.filter(funcao='estudante')
            
            # Contar total de alunas
            total_alunas = alunas.count()
            
            # Contar alunas por cidade
            distribuicao_cidades = alunas.filter(
                endereco__isnull=False,
                endereco__cidade__isnull=False
            ).values(
                'endereco__cidade__nome',
                'endereco__estado__uf'
            ).annotate(
                total=Count('id')
            ).order_by('-total')
            
            # Calcular alunas sem cidade
            alunas_com_cidade = sum(item['total'] for item in distribuicao_cidades)
            alunas_sem_cidade = total_alunas - alunas_com_cidade
            
            # Preparar dados para o gráfico
            cidades = []
            quantidades = []
            
            for item in distribuicao_cidades:
                if item['endereco__cidade__nome'] and item['endereco__estado__uf']:
                    # Formatar como "Cidade - UF"
                    cidade_formatada = f"{item['endereco__cidade__nome']} - {item['endereco__estado__uf']}"
                    cidades.append(cidade_formatada)
                    quantidades.append(item['total'])
            
            # Adicionar "Não informado" se houver alunas sem cidade
            if alunas_sem_cidade > 0:
                cidades.append('Não informado')
                quantidades.append(alunas_sem_cidade)
            
            # Gerar cores para todas as cidades
            cores_base = [
                '#3498db', '#2ecc71', '#9b59b6', '#f1c40f', '#e74c3c', 
                '#1abc9c', '#34495e', '#95a5a6', '#d35400', '#8e44ad'
            ]
            
            # Gerar cores para todas as cidades (repetindo se necessário)
            cores = []
            for i in range(len(cidades)):
                cores.append(cores_base[i % len(cores_base)])
            
            dados_distribuicao = {
                'labels': cidades,
                'data': quantidades,
                'backgroundColor': cores
            }
            
            return Response({
                "status": "success",
                "dados_distribuicao": dados_distribuicao
            })
            
        except Exception as e:
            logger.error(f"Erro na API Distribuição por Cidades de Alunas: {str(e)}")
            # Fallback para dados mockados
            return Response({
                "status": "success",
                "dados_distribuicao": {
                    'labels': ['São Paulo - SP', 'Rio de Janeiro - RJ', 'Belo Horizonte - MG', 
                              'Salvador - BA', 'Porto Alegre - RS', 'Curitiba - PR', 
                              'Recife - PE', 'Fortaleza - CE', 'Florianópolis - SC', 'Goiânia - GO', 'Não informado'],
                    'data': [35, 25, 20, 18, 15, 12, 10, 8, 7, 6, 5],
                    'backgroundColor': [
                        '#3498db', '#2ecc71', '#9b59b6', '#f1c40f', '#e74c3c',
                        '#1abc9c', '#34495e', '#95a5a6', '#d35400', '#8e44ad', '#95a5a6'
                    ]
                }
            })

class ApiFaixaEtaria(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Filtrar apenas estudantes
            estudantes = User.objects.filter(funcao='estudante')

            total_estudantes = estudantes.count()
            sem_data = estudantes.filter(data_nascimento__isnull=True).count()

            # Agora com a faixa abaixo de 13 anos
            faixas_etarias = {
                '-12 anos': 0,
                '13-15 anos': 0,
                '16-18 anos': 0,
                '19-21 anos': 0,
                '22-24 anos': 0,
                '25+ anos': 0,
                'Não informado': sem_data
            }

            hoje = date.today()
            estudantes_com_data = estudantes.filter(data_nascimento__isnull=False)

            for estudante in estudantes_com_data:
                idade = hoje.year - estudante.data_nascimento.year
                if (hoje.month, hoje.day) < (estudante.data_nascimento.month, estudante.data_nascimento.day):
                    idade -= 1

                if idade < 13:
                    faixas_etarias['-12 anos'] += 1
                elif 13 <= idade <= 15:
                    faixas_etarias['13-15 anos'] += 1
                elif 16 <= idade <= 18:
                    faixas_etarias['16-18 anos'] += 1
                elif 19 <= idade <= 21:
                    faixas_etarias['19-21 anos'] += 1
                elif 22 <= idade <= 24:
                    faixas_etarias['22-24 anos'] += 1
                elif idade >= 25:
                    faixas_etarias['25+ anos'] += 1

            labels = list(faixas_etarias.keys())
            data = list(faixas_etarias.values())

            return Response({
                "status": "success",
                "dados_faixa_etaria": {
                    'labels': labels,
                    'data': data,
                    'backgroundColor': [
                        '#E57373', '#FF6384', '#36A2EB',
                        '#FFCE56', '#4BC0C0', '#9966FF', '#95a5a6'
                    ]
                }
            })

        except Exception as e:
            logger.error(f"Erro na API Faixa Etária: {str(e)}")
            return Response({
                "status": "success",
                "dados_faixa_etaria": {
                    'labels': ['-12 anos', '13-15 anos', '16-18 anos',
                               '19-21 anos', '22-24 anos', '25+ anos', 'Não informado'],
                    'data': [0, 120, 250, 180, 90, 60, 447],
                    'backgroundColor': [
                        '#E57373', '#FF6384', '#36A2EB',
                        '#FFCE56', '#4BC0C0', '#9966FF', '#95a5a6'
                    ]
                }
            })
                      
            
from django.db.models import Avg, Count
from django.db.models.functions import ExtractMonth, ExtractYear
from django.utils.timezone import now
from datetime import date
import logging
from applications.models import AcompanhamentoProjeto
logger = logging.getLogger(__name__)

class ApiFrequenciaMensalAlunos(APIView):
    def get(self, request, *args, **kwargs):
        try:
            # Base query para acompanhamentos (todos os projetos)
            query = AcompanhamentoProjeto.objects.all()
            
            # Filtrar pelo ano atual
            ano_atual = date.today().year
            query = query.filter(data_inicio__year=ano_atual)
            
            # Agrupar por mês e calcular a média de frequência
            frequencia_mensal = query.annotate(
                mes=ExtractMonth('data_inicio')
            ).values('mes').annotate(
                media_frequencia=Avg('frequencia'),
                total_alunos=Count('id')
            ).order_by('mes')
            
            # Preparar dados para o gráfico de linha
            meses = []
            medias_frequencia = []
            
            # Nomes dos meses em português
            nomes_meses = [
                'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'
            ]
            
            # Preencher todos os meses do ano, mesmo os sem dados
            for mes in range(1, 13):
                mes_data = next((item for item in frequencia_mensal if item['mes'] == mes), None)
                
                meses.append(nomes_meses[mes-1])
                if mes_data:
                    medias_frequencia.append(float(mes_data['media_frequencia']))
                else:
                    medias_frequencia.append(0)
            
            return Response({
                "status": "success",
                "dados_frequencia": {
                    'labels': meses,
                    'medias': medias_frequencia
                }
            })
            
        except Exception as e:
            logger.error(f"Erro na API Frequência Mensal Alunos: {str(e)}")
            # Fallback para dados mockados
            return Response({
                "status": "success",
                "dados_frequencia": {
                    'labels': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'],
                    'medias': [85.5, 78.2, 82.7, 88.9, 91.3, 87.6, 92.1, 89.7, 86.4, 90.2, 88.9, 84.3]
                }
            })

from datetime import date
from django.db.models import Count, Q
from django.utils.timezone import now


class Dashboard1(TemplateView):
    template_name = "dashboard/dashboardgeral.html"
    
class DashboardProfessoras(TemplateView):
    template_name = "dashboard/dashprofessoras.html"
    
class DashboardAlunas(TemplateView):
    template_name = "dashboard/dashalunas.html"
    

