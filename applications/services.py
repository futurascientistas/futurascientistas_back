from django.utils import timezone
from django.core.exceptions import ValidationError, PermissionDenied
from .models import *
from applications.models import Application


def validar_e_retornar_inscricao(user, pk):
    inscricao = Application.objects.get(pk=pk)

    if 'estudante' in user.roles:
        if inscricao.usuario != user:
            raise PermissionDenied("Você não tem permissão para editar esta inscrição.")
        if inscricao.status not in ['rascunho', 'pendente']:
            raise PermissionDenied("Você só pode editar inscrições com status 'rascunho' ou 'pendente'.")

    elif 'avalidador' in user.roles:
        if inscricao.status != 'avaliacao':
            raise PermissionDenied("Avaliadores só podem editar inscrições com status 'avaliacao'.")

    elif 'admin' not in user.roles:
        raise PermissionDenied("Você não tem permissão para editar inscrições.")

    return inscricao


def atualizar_inscricao(user, instance, validated_data):
    inscricao = validar_e_retornar_inscricao(user, instance.pk)

    status_atual = inscricao.status
    novo_status = validated_data.get('status', status_atual)

    if 'avalidador' in user.roles:
        if novo_status not in ['deferida', 'indeferida', 'pendente']:
            raise PermissionDenied("Status inválido. Você só pode definir como 'Deferida', 'Indeferida' ou 'Pendente'.")

    for attr, value in validated_data.items():
        setattr(inscricao, attr, value)

    if status_atual != novo_status:
        registrar_log_status_inscricao(inscricao, status_atual, novo_status, user)

    inscricao.save()

def inscrever_usuario_em_projeto(user, project_id):
    projeto = Project.objects.get(pk=project_id)
    agora = timezone.now()

    if not (projeto.inicio_inscricoes <= agora <= projeto.fim_inscricoes):
        raise PermissionDenied("Inscrição não permitida: fora do período de inscrição.")

    if Application.objects.filter(usuario=user, projeto=projeto).exists():
        raise PermissionDenied("Você já está inscrita neste projeto.")

    inscricao = Application.objects.create(usuario=user, projeto=projeto)
    
    status_antigo = None
    status_novo = inscricao.status
    
    registrar_log_status_inscricao(inscricao, status_antigo, status_novo, user)
    
    return inscricao


def registrar_log_status_inscricao(inscricao, status_anterior, status_novo, usuario=None):
    def get_status_display(status):
        for choice in Application.STATUS_ESCOLHAS:
            if choice[0] == status:
                return choice[1]
        return status or ""

    modificado_por = f"{usuario.nome} ({usuario.email})" if usuario else None

    if status_anterior != status_novo:
        ApplicationStatusLog.objects.create(
            inscricao=inscricao,
            projeto=inscricao.projeto,
            status_anterior=status_anterior,
            status_novo=status_novo,
            status_anterior_display=get_status_display(status_anterior),
            status_novo_display=get_status_display(status_novo),
            modificado_por=modificado_por,
        )
