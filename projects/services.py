from django.utils import timezone
from django.db import transaction
from .models import *
from core.models import Regiao, Estado, Cidade
from django.db.models import Q
import pandas as pd
import math
import numpy as np

def parse_multivalor(valor):
    if not valor or (isinstance(valor, float) and math.isnan(valor)) or str(valor).strip() == '':
        return []
    itens = [item.strip() for item in str(valor).split(',')]
    return [item for item in itens if item and item.lower() != 'nan']

def preprocess_dataframe(caminho_arquivo):
    df = pd.read_excel(caminho_arquivo)
    df.columns = df.columns.str.strip()
    return df

def registrar_log_status(projeto, status_anterior, status_novo, usuario=None):
    from .models import ProjectStatusLog 

    nome_email = f"{usuario.nome} ({usuario.email})" if usuario else None

    if status_anterior != status_novo:
        ProjectStatusLog.objects.create(
            projeto=projeto,
            status_anterior=status_anterior,
            status_novo=status_novo,
            modificado_por=nome_email
        )

def parse_linha_para_dados(row, campos_validos, campos_datetime):
    dados = {}
    for col in row.index:
        if col not in campos_validos or col in ['id']:
            continue
        valor = row[col]
        if pd.isna(valor) or valor == np.nan:
            dados[col] = None
            continue
        if col in campos_datetime and timezone.is_naive(valor):
            valor = timezone.make_aware(valor, timezone.get_current_timezone())
        dados[col] = valor

    dados['regioes_aceitas'] = parse_multivalor(row.get('regioes_aceitas'))
    dados['estados_aceitos'] = parse_multivalor(row.get('estados_aceitos'))
    dados['cidades_aceitas'] = parse_multivalor(row.get('cidades_aceitas'))
    return dados

def projetos_disponiveis_para_usuario(user):
    hoje = timezone.now().date()
    estado_usuario = getattr(user, 'estado', None)

    projetos = Project.objects.filter(
        ativo=True,
        inicio_inscricoes__lte=hoje,
        fim_inscricoes__gte=hoje,
    ).filter(
        Q(estados_aceitos=None) |  
        Q(estados_aceitos=estado_usuario)  
    ).distinct()

    return projetos

def importar_planilha_projetos(importacao_obj, request):
    df = preprocess_dataframe(importacao_obj.arquivo.path)
    campos_validos = [f.name for f in Project._meta.get_fields()]
    campos_datetime = ['data_inicio', 'data_fim', 'inicio_inscricoes', 'fim_inscricoes']

    ignoradas = []
    total_linhas = len(df)
    projetos_criados = 0

    todas_regioes = Regiao.objects.all()
    todos_estados = Estado.objects.all()
    todas_cidades = Cidade.objects.select_related('estado__regiao').all()

    def filtrar_objs(model_objs, nomes, campos_lookup):
        if not nomes:
            return model_objs.none()
        queries = Q()
        for val in nomes:
            q = Q()
            for campo in campos_lookup:
                q |= Q(**{f"{campo}__iexact": val})
            queries |= q
        return model_objs.filter(queries).distinct()

    with transaction.atomic():
        for index, row in df.iterrows():
            try:
                dados = parse_linha_para_dados(row, campos_validos, campos_datetime)
                regioes = dados.pop('regioes_aceitas', [])
                estados = dados.pop('estados_aceitos', [])
                cidades = dados.pop('cidades_aceitas', [])

                # Cria o projeto já validado
                projeto = Project.objects.create(**dados)

                # Ajusta ManyToMany 
                regioes_objs = filtrar_objs(todas_regioes, regioes, ['nome', 'abreviacao'])
                estados_objs = filtrar_objs(todos_estados, estados, ['nome', 'uf'])
                cidades_objs = filtrar_objs(todas_cidades, cidades, ['nome', 'estado__regiao__nome', 'estado__regiao__abreviacao'])

                projeto.regioes_aceitas.set(regioes_objs)
                projeto.estados_aceitos.set(estados_objs)
                projeto.cidades_aceitas.set(cidades_objs)

                # Log de status
                registrar_log_status(
                    projeto=projeto,
                    status_anterior=None,
                    status_novo=projeto.status,
                    usuario=request.user
                )

                projetos_criados += 1

            except Exception as e:
                ignoradas.append(
                    f"Linha {index + 2} - não processada\n"
                    f"    Conteúdo: {locals().get('dados', {})}\n"
                    f"    Motivo: {str(e)}\n"
                )

        # Atualiza resumo da importação
        importacao_obj.linhas_lidas = total_linhas
        importacao_obj.projetos_criados = projetos_criados
        importacao_obj.projetos_ignorados = len(ignoradas)
        importacao_obj.linhas_ignoradas_texto = "\n".join(ignoradas)
        importacao_obj.save()
