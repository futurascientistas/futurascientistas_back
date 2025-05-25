from django.utils import timezone
from django.core.exceptions import ValidationError, PermissionDenied
from .models import Application, Project
from applications.models import Application


def validar_e_retornar_inscricao(user, pk):
    inscricao = Application.objects.get(pk=pk)

    if user.role == 'estudante':
        if inscricao.usuario != user:
            raise PermissionDenied("Você não tem permissão para editar esta inscrição.")
        if inscricao.status not in ['rascunho', 'pendente']:
            raise ValidationError("Você só pode editar inscrições com status 'rascunho' ou 'pendente'.")
    
    elif user.role == 'avaliadora':
        if inscricao.status != 'avaliacao':
            raise ValidationError("Avaliadores só podem editar inscrições com status 'avaliacao'.")
    
    else:
        raise PermissionDenied("Você não tem permissão para editar inscrições.")

    return inscricao


def atualizar_inscricao(user, instance, validated_data):
    status_atual = instance.status
    novo_status = validated_data.get('status', status_atual)

    if user.role == 'avaliadora':
        if status_atual != 'avaliacao':
            raise ValidationError("Só é possível avaliar inscrições com status 'avaliacao'.")
        if novo_status not in ['deferida', 'indeferida', 'pendente']:
            raise ValidationError("Status inválido. Você só pode definir como 'Deferida', 'Indeferida' ou 'Pendente'.")

    elif user.role == 'estudante':
        if 'status' in validated_data and validated_data['status'] != status_atual:
            raise ValidationError("Você não tem permissão para alterar o status da inscrição.")

    else:
        raise PermissionDenied("Permissão negada para editar esta inscrição.")

    for attr, value in validated_data.items():
        setattr(instance, attr, value)

    instance.save()

def inscrever_usuario_em_projeto(user, project_id):
    projeto = Project.objects.get(pk=project_id)
    agora = timezone.now()

    if not (projeto.inicio_inscricoes <= agora <= projeto.fim_inscricoes):
        raise ValidationError("Inscrição não permitida: fora do período de inscrição.")

    if Application.objects.filter(usuario=user, projeto=projeto).exists():
        raise ValidationError("Você já está inscrita neste projeto.")

    inscricao = Application.objects.create(usuario=user, projeto=projeto)
    return inscricao