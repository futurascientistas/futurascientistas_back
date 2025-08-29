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
from users.models.school_transcript_model import HistoricoEscolar
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
                    if formset.is_valid():
                        formset.save()
                        messages.success(request, 'Histórico escolar atualizado com sucesso! 📝')
                        is_valid = True
                    else:
                        logger.error(f"Erro na validação do histórico escolar. Por favor, corrija os erros abaixo: {formset.errors}")
                        messages.error(request, 'Erro na validação do histórico escolar. Por favor, corrija os erros abaixo.')

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
    formset = HistoricoNotaFormSet(instance=historico,  prefix="notas")

    if user.funcao == 'professora':
        campos_estudante = ['historico_escolar', 'telefone_responsavel', 'comprovante_autorizacao_responsavel', 'comprovante_autorizacao_responsavel__upload', 'comprovante_autorizacao_responsavel__clear']
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
        'user': user,
        'steps': steps,
    }

    current_step_from_url = int(request.GET.get('step', 1))
    
    context['current_step'] = current_step_from_url

    return render(request, 'components/users/perfil.html', context)




from django.views import View
from django.http import JsonResponse
from users.models.user_model import User
from projects.models import Project
from django.db.models import Q, Count


class ApiAlunasDatas(APIView):
    def get(self, request, *args, **kwargs):
        usuarios_qs = User.objects.all()
        
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
        professores_qs = User.objects.filter(is_staff=True)
       
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

        return Response({
            "mensagem": "ok",
            "projetos_em_andamento": dados
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
        
