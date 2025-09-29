import magic
import mimetypes
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
from django.http import HttpResponseForbidden
from users.permissions import *
from .models import *
from .services import *
from django.contrib import messages
from .forms import *
from django.contrib.auth.decorators import login_required
from .services import inscrever_usuario_em_projeto
from django.db import transaction
from django.utils import timezone
from .models import Application
from .forms import ApplicationProfessorForm
from django.template.loader import render_to_string


def _is_periodo_inscricao_aberto():
    hoje = timezone.now().date()
    ano_atual = hoje.year
    inicio_inscricao = timezone.datetime(ano_atual, 1, 1).date()
    fim_inscricao = timezone.datetime(ano_atual, 12, 31).date()
    return inicio_inscricao <= hoje <= fim_inscricao

@login_required
def minhas_inscricoes(request):
    inscricoes = Application.objects.filter(usuario=request.user).order_by('-criado_em')  
    ano_atual = timezone.now().year
    tem_inscricao_ano_atual = inscricoes.filter(criado_em__year=ano_atual).exists()
    periodo_inscricao_aberto = _is_periodo_inscricao_aberto()
    
    return render(
        request,
        "components/applications/minhas_inscricoes.html",
        {
            "inscricoes": inscricoes,
            "tem_inscricao_ano_atual": tem_inscricao_ano_atual,
            'periodo_inscricao_aberto': periodo_inscricao_aberto,
        }
    )

@login_required
def inscricao_aluna(request, inscricao_id=None):
    ano_atual = timezone.now().year
    current_step = int(request.POST.get("current_step", 1))

    steps = [
        {"number": 1, "name": "Endereço"},
        {"number": 2, "name": "Projeto"},
        {"number": 3, "name": "Informações e Experiência"},
        {"number": 4, "name": "Documentos"},
        {"number": 5, "name": "Revisão e Envio"},
    ]

    # campos por step
    step_fields = {
        1: ["cep", "rua", "numero", "cidade", "estado"],
        2: [
            "projeto",
            "tipo_de_vaga",
        ],
        3: ["tamanho_jaleco", 
            "tipo_deficiencia",
            "necessita_material_especial",
            "tipo_material_necessario"],
        4: ["drive_rg_frente__upload",
            "drive_rg_verso__upload",
            "drive_cpf_anexo__upload",
            "drive_declaracao_inclusao__upload"],
        5: ["aceite_declaracao_veracidade","aceite_requisitos_tecnicos"],
    }

    if inscricao_id:
        instance = get_object_or_404(
            Application.objects.select_related("usuario__endereco", "projeto"),
            id=inscricao_id,
            usuario=request.user
        )
    else:
        instance = (
            Application.objects
            .filter(usuario=request.user, criado_em__year=ano_atual)
            .select_related("usuario__endereco", "projeto")
            .first()
        )
        
    if request.method == "POST":

        form = ApplicationAlunoForm(
            request.POST, 
            request.FILES,
            user=request.user, 
            instance=instance,
            current_step=current_step, 
            step_fields=step_fields
        )
        
        acao = request.POST.get("acao")

        if "auto_upload_field" in request.POST:
            return _handle_auto_upload(request, form)
        
        if "auto_clear_field" in request.POST:
            return _handle_auto_clear(request, form)

        try:
            with transaction.atomic():
                if acao == "proximo":
                    if form.is_valid():
                        instance = _save_as_draft(form, request, instance, step_fields[current_step])
                        current_step = _next_step_if_valid(form, current_step, steps, step_fields)
                        form = ApplicationAlunoForm(
                            user=request.user,
                            instance=instance,
                            current_step=current_step,
                            step_fields=step_fields
                        )
                elif acao == "voltar":
                    current_step = max(current_step - 1, 1)
                    if instance and instance.pk:
                        instance.refresh_from_db()
                    form = ApplicationAlunoForm(
                        user=request.user,
                        instance=instance,
                        current_step=current_step,
                        step_fields=step_fields
                    )
                elif acao in {"salvar", "enviar"}:
                    try:

                        _handle_save_or_submit(request, form, instance, acao, current_step, step_fields)
                        
                        if acao == "enviar" and form.is_valid():
                            return redirect("/inscricoes/minhas-inscricoes/")
                        
                    except PermissionDenied as e:
                        messages.error(request, str(e))
                    
            if instance and instance.pk:
                instance.refresh_from_db()       

        except Exception as e:
            logger.error(f"Erro inesperado: {e}", exc_info=True)
            messages.error(request, "Ocorreu um erro inesperado. Tente novamente.")
    else:
        if not instance:
            instance = Application(usuario=request.user)

        form = ApplicationAlunoForm(
            user=request.user, 
            instance=instance, 
            current_step=current_step,
            step_fields=step_fields
        )

    current_step_fields = [
        (name, form[name])
        for name in step_fields.get(current_step, [])
        if name in form.fields
    ]
    
    step_title = next((s["name"] for s in steps if s["number"] == current_step), "")

    return render(
        request,
        "components/applications/student_application_form.html",
        {
            "form": form,
            "steps": steps,
            "current_step": current_step,
            "current_step_fields": current_step_fields,
            "step_title": step_title,
            "steps_with_save": [2, 3, 4, 5],
        },
    )

@login_required
def inscricao_professora(request, inscricao_id=None):
    ano_atual = timezone.now().year
    current_step = int(request.POST.get("current_step", 1))

    steps = [
        {"number": 1, "name": "Endereço"},
        {"number": 2, "name": "Projeto"},
        {"number": 3, "name": "Informações e Experiência"},
        {"number": 4, "name": "Documentos"},
        {"number": 5, "name": "Revisão e Envio"},
    ]

    # campos por step
    step_fields = {
        1: ["cep", "rua", "numero", "cidade", "estado"],
        2: [
            "projeto",
            "numero_edicoes_participadas",
            "titulo_projeto_submetido",
            "link_projeto",
            "como_soube_programa",
        ],
        3: ["grau_formacao","area_atuacao","docencia_superior","docencia_medio",
            "orientacoes_estudantes","participacoes_bancas","periodico_indexado",
            "livro_publicado","capitulo_publicado","anais_congresso",
            "apresentacao_oral","orientacao_ic","feira_ciencias","curso_extensao",
            "curso_capacitacao","premiacoes","missao_cientifica","tamanho_jaleco",
            "tipo_de_vaga","tipo_deficiencia", "necessita_material_especial",
            "tipo_material_necessario"],

        4: ["curriculo_lattes_url",
            "drive_documentacao_comprobatoria_lattes__upload",
            "drive_declaracao_vinculo__upload",
            "drive_rg_frente__upload",
            "drive_rg_verso__upload",
            "drive_cpf_anexo__upload",
            "drive_declaracao_inclusao__upload"],
        5: ["aceite_declaracao_veracidade","aceite_requisitos_tecnicos"],
    }

    if inscricao_id:
        instance = get_object_or_404(
            Application.objects.select_related("usuario__endereco", "projeto"),
            id=inscricao_id,
            usuario=request.user
        )
    else:
        instance = (
            Application.objects
            .filter(usuario=request.user, criado_em__year=ano_atual)
            .select_related("usuario__endereco", "projeto")
            .first()
        )
        
    if request.method == "POST":

        form = ApplicationProfessorForm(
            request.POST, 
            request.FILES,
            user=request.user, 
            instance=instance,
            current_step=current_step, 
            step_fields=step_fields
        )
        
        acao = request.POST.get("acao")

        if "auto_upload_field" in request.POST:
            return _handle_auto_upload(request, form)
        
        if "auto_clear_field" in request.POST:
            return _handle_auto_clear(request, form)

        try:
            with transaction.atomic():
                if acao == "proximo":
                    if form.is_valid():
                        instance = _save_as_draft(form, request, instance, step_fields[current_step])
                        current_step = _next_step_if_valid(form, current_step, steps, step_fields)
                        form = ApplicationProfessorForm(
                            user=request.user,
                            instance=instance,
                            current_step=current_step,
                            step_fields=step_fields
                        )
                elif acao == "voltar":
                    current_step = max(current_step - 1, 1)
                    if instance and instance.pk:
                        instance.refresh_from_db()
                    form = ApplicationProfessorForm(
                        user=request.user,
                        instance=instance,
                        current_step=current_step,
                        step_fields=step_fields
                    )
                elif acao in {"salvar", "enviar"}:
                    try:

                        _handle_save_or_submit(request, form, instance, acao, current_step, step_fields)
                        
                        if acao == "enviar" and form.is_valid():
                            return redirect("/inscricoes/minhas-inscricoes/")
                        
                    except PermissionDenied as e:
                        messages.error(request, str(e))
                    
            if instance and instance.pk:
                instance.refresh_from_db()       

        except Exception as e:
            logger.error(f"Erro inesperado: {e}", exc_info=True)
            messages.error(request, "Ocorreu um erro inesperado. Tente novamente.")
    else:
        if not instance:
            instance = Application(usuario=request.user)

        form = ApplicationProfessorForm(
            user=request.user, 
            instance=instance, 
            current_step=current_step,
            step_fields=step_fields
        )

    current_step_fields = [
        (name, form[name])
        for name in step_fields.get(current_step, [])
        if name in form.fields
    ]
    
    step_title = next((s["name"] for s in steps if s["number"] == current_step), "")

    return render(
        request,
        "components/applications/professor_application_form.html",
        {
            "form": form,
            "steps": steps,
            "current_step": current_step,
            "current_step_fields": current_step_fields,
            "step_title": step_title,
            "steps_with_save": [2, 3, 4, 5],
        },
    )

def _handle_auto_upload(request, form):
    field_name = request.POST.get("auto_upload_field")
    if not field_name:
        return JsonResponse({"success": False, "error": "Campo não informado"}, status=400)
    
    for f in form.fields:
        if f.endswith("__upload") and f != field_name:
            form.fields[f].required = False

    form.full_clean() 
    if field_name not in form.cleaned_data:
        errors = form.errors.get(field_name, ["Erro de validação desconhecido."])
        return JsonResponse({"success": False, "error": errors[0]}, status=400)
        
    try:
        instance = form.save(commit=True, auto_upload_field=field_name) 
        if instance.pk:

            try:
                instance.refresh_from_db(fields=[field_name.replace("__upload", "")])
            except Exception:
                instance = Application.objects.get(pk=instance.pk)

        new_form = ApplicationProfessorForm(
            user=form.user,
            instance=instance,
            current_step=form.current_step,
            step_fields=form.step_fields
        )

        field = new_form[field_name]

        rendered = render_to_string("components/applications/form_field.html", {"field": field, "form":new_form}, request=request)
        return JsonResponse({"success": True, "html": rendered, "field_name": field_name})
        
    except forms.ValidationError as ve:
        return JsonResponse({"success": False, "error": str(ve)}, status=400)
    except Exception as e:
        logger.error(f"Erro no auto-upload para o campo {field_name}: {e}", exc_info=True)
        return JsonResponse({"success": False, "error": "Erro ao enviar o arquivo. Tente novamente mais tarde."}, status=500)

def _handle_auto_clear(request, form):
    field_name = request.POST.get("auto_clear_field")
    if not field_name:
        return JsonResponse({"success": False, "error": "Campo não informado"}, status=400)

    try:
        instance = form.instance
        drive_service = DriveService()

        model_field_name = field_name.replace("__clear", "")
        file_id = getattr(instance, model_field_name, None)

        if file_id:
            try:
                drive_service.delete_file(file_id)
            except Exception as e:
                logger.error(f"Erro ao remover arquivo do Drive ({model_field_name}): {e}", exc_info=True)

        setattr(instance, model_field_name, None)

        if instance.pk:
            instance.save(update_fields=[model_field_name])

        new_form = ApplicationProfessorForm(
            user=form.user,
            instance=instance,
            current_step=form.current_step,
            step_fields=form.step_fields
        )

        field = new_form[model_field_name + "__upload"]
        rendered = render_to_string("components/applications/form_field.html", {"field": field,"drive_link": None}, request=request)

        return JsonResponse({"success": True, "html": rendered, "field_name": field_name})

    except Exception as e:
        logger.error(f"Erro no auto-clear para o campo {field_name}: {e}", exc_info=True)
        return JsonResponse({"success": False, "error": "Erro ao remover arquivo. Tente novamente mais tarde."}, status=500)


def _next_step_if_valid(form, current_step, steps, step_fields):
    campos_step = step_fields.get(current_step, set())
    erros_do_step = [f for f in form.errors if f in campos_step]
    if not erros_do_step:
        return min(current_step + 1, len(steps))
    
    return current_step

def _save_as_draft(form, request, instance, step_fields):

    if not instance or not instance.pk:
        instance = Application(usuario=request.user)

    instance.usuario = request.user

    if not hasattr(form, "cleaned_data"):
        form.full_clean()

    campos_a_salvar = set()

    for field_name in step_fields:
        if field_name.endswith("__upload"):
            continue

        if field_name not in form.fields or field_name not in form.fields:
            continue

        if field_name not in form.cleaned_data:
            continue

        valor = form.cleaned_data.get(field_name)

        # if field_name in ["rua", "numero", "cep", "estado", "cidade"]:
        #     endereco = getattr(instance.usuario, "endereco", None)
        #     if not endereco:
        #         endereco = Endereco.objects.create(usuario=instance.usuario)
        #         instance.usuario.endereco = endereco
        #         instance.usuario.save(update_fields=["endereco"])
        #     setattr(endereco, field_name, valor)
        #     endereco.save()
        #     continue

        setattr(instance, field_name, valor)
        campos_a_salvar.add(field_name)

    instance.status = "rascunho"
    campos_a_salvar.add("status")

    if campos_a_salvar:
        instance.save(update_fields=list(campos_a_salvar))
    else:
        instance.save()

    instance.refresh_from_db()

    return instance


def _handle_save_or_submit(request, form, instance, acao, current_step=None, step_fields=None):
    
    if current_step and step_fields:
        instancia = _save_as_draft(form, request, instance, step_fields[current_step])
    else:
        instancia = _save_as_draft(form, request, instance, [])

    if acao == "salvar":

        registrar_log_status_inscricao(
            instancia,
            instance.status if instance else None,
            "rascunho",
            request.user
        )
        messages.success(request, "Inscrição salva como rascunho.")
        return

    instance.refresh_from_db()
    
    data = {}
    for field_name in form.Meta.fields:
        value = getattr(instance, field_name)
        if value is not None:
            if hasattr(value, 'pk'):
                value = value.pk
            data[field_name] = value

    form = ApplicationProfessorForm(
        data=data,
        files=request.FILES,
        user=request.user,
        instance=instance,
        current_step=current_step,
        step_fields=step_fields
    )

    if not form.is_valid():
        messages.error(request, "Por favor corrija os erros no formulário.")
        return

    instancia = form.save(commit=False)
    projeto = form.cleaned_data.get("projeto")

    agora = timezone.now().date()

    try:
        if projeto and not (projeto.inicio_inscricoes <= agora <= projeto.fim_inscricoes):
            raise PermissionDenied("Fora do período de inscrição.")
        
        if Application.objects.filter(usuario=request.user, projeto=projeto).exclude(pk=instancia.pk).exists():
            raise PermissionDenied("Você já está inscrita neste projeto.")

        validar_unica_inscricao_no_ciclo(request.user, projeto)

    except PermissionDenied as e:

        status_antigo = instancia.status if instance else None
        instancia.status = "inválida"
        instancia.usuario = request.user
        instancia.save()

        raise PermissionDenied(str(e))
    
    status_antigo = instancia.status if instance else None
    instancia.status = "avaliacao" if acao == "enviar" else "rascunho"
    instancia.usuario = request.user
    instancia.save()
    
    registrar_log_status_inscricao(instancia, status_antigo, instancia.status, request.user)

    msg = "Inscrição enviada com sucesso!" if acao == "enviar" else "Inscrição salva como rascunho."
    messages.success(request, msg)

@login_required
def editar_inscricao(request, inscricao_id):
    inscricao = get_object_or_404(Application, id=inscricao_id, usuario=request.user)

    # Verifica se o usuário é dono da inscrição ou admin
    if not (inscricao.usuario == request.user or request.user.is_staff or request.user.is_superuser):
        return HttpResponseForbidden("Você não tem permissão para visualizar essa inscrição.")
    
    if 'professora' in inscricao.usuario.roles:
        return redirect("application:editar_inscricao_professora", inscricao_id=inscricao.id)
    else:
        return redirect("application:editar_inscricao_aluna", inscricao_id=inscricao.id)


@login_required
def visualizar_inscricao(request, inscricao_id):
    inscricao = get_object_or_404(Application, id=inscricao_id, usuario=request.user)

    # Verifica se o usuário é dono da inscrição ou admin
    if not (inscricao.usuario == request.user or request.user.is_staff or request.user.is_superuser):
        return HttpResponseForbidden("Você não tem permissão para visualizar essa inscrição.")

    # Verifica qual form usar
    if 'professora' in inscricao.usuario.roles:
        form = ApplicationProfessorForm(instance=inscricao, user=request.user)
        template_name = 'components/applications/professor_application_view.html'
    else:
        form = ApplicationAlunoForm(instance=inscricao, user=request.user)
        template_name = 'components/applications/student_application_view.html'

    # Deixa todos os campos como somente leitura
    for f in form.fields.values():
        f.disabled = True

    comentarios = Comentario.objects.filter(aplicacao=inscricao).order_by('-criado_em')

    if request.method == 'POST':
        comentario_form = ComentarioForm(request.POST)
        if comentario_form.is_valid():
            comentario = comentario_form.save(commit=False)
            comentario.usuario = request.user
            comentario.aplicacao = inscricao
            comentario.save()
            return redirect('application:visualizar_inscricao', inscricao_id=inscricao.id)
    else:
        comentario_form = ComentarioForm()

    return render(request, template_name, {
        'form': form,
        'comentarios': comentarios,
        'comentario_form': comentario_form,
        'readonly': True,
    })

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