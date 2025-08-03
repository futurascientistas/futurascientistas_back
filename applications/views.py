from rest_framework import generics, status,permissions
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .services import validar_e_retornar_inscricao, atualizar_inscricao
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .serializers import ApplicationSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from users.permissions import *
from .models import *
import magic
import mimetypes


from .serializers import ApplicationSerializer
from .services import inscrever_usuario_em_projeto

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
    





# ------------------------------------------------------------


# apps/applications/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DetailView, ListView
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Application
from .forms import ApplicationForm


class ApplicationListView(LoginRequiredMixin, ListView):
    model = Application
    template_name = "applications/application_list.html"
    context_object_name = "applications"
    paginate_by = 20

    def get_queryset(self):
        qs = (Application.objects
              .select_related("projeto", "usuario")
              .order_by("-atualizado_em"))
        # Exemplo simples: usuário vê as próprias inscrições; admin/superuser vê todas
        if not self.request.user.is_superuser:
            qs = qs.filter(usuario=self.request.user)
        # Filtro por status (opcional)
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        search = self.request.GET.get("q")
        if search:
            qs = qs.filter(
                Q(projeto__titulo__icontains=search) |
                Q(observacoes__icontains=search)
            )
        return qs


class ApplicationCreateView(LoginRequiredMixin, CreateView):
    model = Application
    form_class = ApplicationForm
    template_name = "applications/application_form.html"
    success_url = reverse_lazy("applications:list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request  # usado para log
        return kwargs

    def form_valid(self, form: ApplicationForm):
        form.instance.usuario = self.request.user  # owner
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        form = ctx["form"]
        ctx["binary_uploads"] = [
            {
                "name": name,
                "label": label,
                "upload": form[f"{name}__upload"],  # BoundField
                "clear": form[f"{name}__clear"],    # BoundField
            }
            for name, label in form.binary_file_fields.items()
        ]
        return ctx


class ApplicationUpdateView(LoginRequiredMixin, UpdateView):
    model = Application
    form_class = ApplicationForm
    template_name = "applications/application_form.html"
    success_url = reverse_lazy("applications:list")

    def get_queryset(self):
        qs = Application.objects.all()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(usuario=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class ApplicationDetailView(LoginRequiredMixin, DetailView):
    model = Application
    template_name = "applications/application_detail.html"
    context_object_name = "application"

    def get_queryset(self):
        qs = Application.objects.select_related("projeto", "usuario").prefetch_related("logs_status")
        if self.request.user.is_superuser:
            return qs
        return qs.filter(usuario=self.request.user)





# apps/applications/views.py
from django.http import Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.encoding import iri_to_uri
from django.views.decorators.http import require_GET
import mimetypes

from .models import Application
from .forms import ApplicationForm  # para reaproveitar a lista de campos binários

ALLOWED_BINARY_FIELDS = tuple(ApplicationForm.BINARY_FILE_FIELDS.keys())

@require_GET
def download_application_file(request, pk: str, field: str):
    # segurança: só permite campos conhecidos
    if field not in ALLOWED_BINARY_FIELDS:
        raise Http404("Arquivo não encontrado.")

    try:
        app = Application.objects.get(pk=pk)
    except Application.DoesNotExist:
        raise Http404("Inscrição não encontrada.")

    # autorização: dono ou superuser
    if not (request.user.is_superuser or app.usuario_id == request.user.id):
        raise Http404("Arquivo não encontrado.")

    blob = getattr(app, field)
    if not blob:
        raise Http404("Arquivo não encontrado.")

    # não temos nome/tipo original; defina um nome padrão
    filename = f"{field}.bin"
    content_type, _ = mimetypes.guess_type(filename)
    if not content_type:
        content_type = "application/octet-stream"

    resp = HttpResponse(bytes(blob), content_type=content_type)
    resp["Content-Disposition"] = f'attachment; filename="{iri_to_uri(filename)}"'
    return resp
