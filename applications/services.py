from django.utils import timezone
from django.core.exceptions import ValidationError, PermissionDenied
from .models import *
from django.db import transaction
from applications.models import Application
from django.http import JsonResponse
from django.db.models import Q

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

def validar_unica_inscricao_no_ciclo(user, projeto):
    print("Validando inscrição única no ciclo para o usuário:", user, "e projeto:", projeto)
    

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

def inscrever_usuario_em_projeto(user, project_id, dados=None, arquivos=None):
    projeto = Project.objects.get(pk=project_id)
    agora = timezone.now()

    if not (projeto.inicio_inscricoes <= agora <= projeto.fim_inscricoes):
        raise PermissionDenied("Inscrição não permitida: fora do período de inscrição.")
    
    if Application.objects.filter(usuario=user, projeto=projeto).exists():
        raise PermissionDenied("Você já está inscrita neste projeto.")
    
    validar_unica_inscricao_no_ciclo(user, projeto)

    inscricao = Application(usuario=user, projeto=projeto)

    if dados:
        for attr, value in dados.items():
            setattr(inscricao, attr, value)

    if arquivos:
        for attr, file in arquivos.items():
            if hasattr(file, 'read'):
                setattr(inscricao, attr, file.read())

    inscricao.save()

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

@transaction.atomic
def calcular_ranking(inscricao):
    ranking = 0.0

    # I. Perfil Acadêmico (Máximo 4,0 pontos)
    grau = inscricao.grau_formacao  

    if grau == GrauFormacao.DOUTORADO:
        perfil = 4.0
    elif grau == GrauFormacao.MESTRADO:
        perfil = 3.0
    elif grau == GrauFormacao.ESPECIALIZACAO:
        perfil = 2.0
    elif grau in [GrauFormacao.LICENCIATURA, GrauFormacao.BACHARELADO, GrauFormacao.GRADUACAO]:
        perfil = 1.0
    else:
        perfil = 0.0

    # II. Atividade Docente (Máximo 4,0 pontos)
    docente = 0.0
    docente += min(float(inscricao.docencia_superior or 0) * 0.2, 1.0)       # 0.2 ponto por semestre
    docente += min(float(inscricao.docencia_medio or 0) * 0.2, 1.0)          # 0.2 ponto por ano
    docente += min(float(inscricao.orientacao_ic or 0) * 0.2, 1.0)           # 0.2 ponto por ano
    if inscricao.feira_ciencias:
        docente += 0.2                                                       # 0.2 ponto por evento

    docente = min(docente, 4.0)
    ranking += docente

    # III. Atividade de Pesquisa (a preencher conforme critérios)
    pesquisa = 0.0
    # Exemplo: pesquisa += ...
    pesquisa = min(pesquisa, 4.0)
    ranking += pesquisa

    # IV. Outras Atividades (a preencher conforme critérios)
    outras = 0.0
    # Exemplo: outras += ...
    outras = min(outras, 1.0)
    ranking += outras

    # Atualiza os campos na inscrição
    inscricao.ranking = ranking
    inscricao.perfil_academico_pontuacao = perfil
    inscricao.atividade_docente_pontuacao = docente
    inscricao.atividade_pesquisa_pontuacao = pesquisa
    inscricao.outras_atividades_pontuacao = outras

    inscricao.save()

def calcular_ranking_todas_professoras(projeto):
    inscricoes_professoras = Application.objects.filter(
        projeto=projeto,
        usuario__groups__name='professora' 
    )

    for inscricao in inscricoes_professoras:
        calcular_ranking.delay(inscricao.id)

def filtrar_cidade_estado(request):
    cidade_id = request.GET.get('cidade')
    estado_id = request.GET.get('estado')
    remoto = request.GET.get('remoto')
    user = request.user  
    projetos = Project.objects.all()

    try:
        filtros = Q(eh_remoto=True)
        if cidade_id:
            filtros |= Q(cidades_aceitas__id=cidade_id)
        if estado_id:
            filtros |= Q(estados_aceitos__id=estado_id)

        projetos = projetos.filter(filtros).distinct()
        print(projetos)

        lista = []
        for p in projetos:
            lista.append({
                'id': p.id,
                'nome': p.nome,
                'remoto': p.eh_remoto,
                'cidade': p.cidades_aceitas.first().nome if p.cidades_aceitas.exists() else '',
                'estado': p.estados_aceitos.first().nome if p.estados_aceitos.exists() else '',
            })
        
        return JsonResponse({'dados': lista})

    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)