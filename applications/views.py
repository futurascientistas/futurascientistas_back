from rest_framework import generics, status,permissions
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .services import validar_e_retornar_inscricao, atualizar_inscricao
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404, render, redirect
from .serializers import ApplicationSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from users.permissions import *
from .models import *
import magic
import mimetypes
from django.contrib import messages
from .forms import *
from .models import Project
from django.contrib.auth.decorators import login_required

from .serializers import ApplicationSerializer
from .services import inscrever_usuario_em_projeto



@login_required
def inscricao_professora(request):
    ano_atual = timezone.now().year

    inscricoes_ano = Application.objects.filter(
        usuario=request.user,
        criado_em__year=ano_atual
    )

    if inscricoes_ano.exists():
        return render(request, 'components/applications/minhas_inscricoes.html', {'inscricoes': inscricoes_ano})

    if request.method == 'POST':
        form = ApplicationProfessorForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save(commit=False)
            app.usuario = request.user
            app.save()
            messages.success(request, "Inscrição enviada com sucesso!")
            return redirect('dashboard')
        else:
            messages.error(request, "Por favor corrija os erros no formulário.")
    else:
        form = ApplicationProfessorForm()

    return render(request, 'components/applications/professor_application_form.html', {'form': form})


@login_required

def minhas_inscricoes(request):
    inscricoes = Application.objects.filter(usuario=request.user).order_by('-criado_em')  
    
    return render(request, 'components/applications/minhas_inscricoes.html', {'inscricoes': inscricoes})

@login_required
def editar_inscricao(request, inscricao_id):
    inscricao = get_object_or_404(Application, id=inscricao_id, usuario=request.user)

    if request.method == "POST":
        form = ApplicationProfessorForm(request.POST, request.FILES, instance=inscricao)
        if form.is_valid():
            instancia = form.save(commit=False)

            acao = request.POST.get('acao')
                
            if acao == 'enviar':
                instancia.status = 'avaliacao'  
            elif acao == 'salvar':
                instancia.status = 'rascunho'  
            
            instancia.save()
            messages.success(request, "Inscrição atualizada com sucesso!")
            return redirect('application:minhas_inscricoes')
        else:
            messages.error(request, "Por favor, corrija os erros.")
    else:
        form = ApplicationProfessorForm(instance=inscricao)

    return render(request, 'components/applications/professor_application_form.html', {'form': form})


def inscricao_aluna(request):
    if request.method == 'POST':
        form = ApplicationAlunoForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save(commit=False)
            app.usuario = request.user
            app.save()
            messages.success(request, "Inscrição enviada com sucesso!")
            return redirect('home')  
        else:
            messages.error(request, "Por favor corrija os erros no formulário.")
    else:
        form = ApplicationAlunoForm()

    return render(request, 'components/applications/student_application_form.html', {'form': form})

class InscreverProjetoView(generics.CreateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        user = request.user
        project_id = self.kwargs.get('project_id')

        try:
            dados = request.data.copy()
            arquivos = request.FILES

            for campo in ['usuario', 'projeto', 'id', 'criado_em']:
                dados.pop(campo, None)

            application = inscrever_usuario_em_projeto(user, project_id, dados=dados, arquivos=arquivos)
            serializer = self.get_serializer(instance=application)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({"detail": e.message if hasattr(e, 'message') else str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        
class EditarInscricaoView(generics.UpdateAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrAvaliadora]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return validar_e_retornar_inscricao(self.request.user, self.kwargs["application_id"])


    def perform_update(self, serializer):
        atualizar_inscricao(self.request.user, serializer.instance, serializer.validated_data)


class AnexoDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, inscricao_id, campo):
        app = get_object_or_404(Application, pk=inscricao_id)

        if request.user != app.usuario and 'admin' not in request.user.roles and 'avalidador' not in request.user.roles:
            return HttpResponse("Acesso negado", status=403)

        arquivo = getattr(app, campo, None)
        if not arquivo:
            return HttpResponse("Campo ou arquivo inválido", status=404)

        if isinstance(arquivo, memoryview):
            arquivo = arquivo.tobytes()

        mime_type = magic.Magic(mime=True).from_buffer(arquivo)
        ext = mimetypes.guess_extension(mime_type) or ".bin"
        filename = f"{campo}{ext}"

        return HttpResponse(arquivo, content_type=mime_type, headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        })