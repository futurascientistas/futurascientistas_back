from django.utils import timezone
from django.db import transaction
from .models import Project
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

def importar_planilha_projetos(importacao_obj):
    df = preprocess_dataframe(importacao_obj.arquivo.path)
    campos_validos = [f.name for f in Project._meta.get_fields()]
    campos_datetime = ['data_inicio', 'data_fim', 'inicio_inscricoes', 'fim_inscricoes']

    projetos = []
    regioes_aceitas_list = []
    estados_aceitos_list = []
    cidades_aceitas_list = []
    ignoradas = []
    total_linhas = len(df)

    for index, row in df.iterrows():
        try:
            dados = parse_linha_para_dados(row, campos_validos, campos_datetime)
            regioes = dados.pop('regioes_aceitas', [])
            estados = dados.pop('estados_aceitos', [])
            cidades = dados.pop('cidades_aceitas', [])

            projeto = Project(**dados)
            projeto.full_clean()

            projetos.append(projeto)
            regioes_aceitas_list.append(regioes)
            estados_aceitos_list.append(estados)
            cidades_aceitas_list.append(cidades)

        except Exception as e:
            ignoradas.append(
                f"Linha {index + 2} - não processada\n"
                f"    Conteúdo: {dados}\n"
                f"    Motivo: {str(e)}\n"
            )

    with transaction.atomic():
        Project.objects.bulk_create(projetos)
        projetos_criados = Project.objects.order_by('-id')[:len(projetos)][::-1]

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

        for proj, reg_names, est_names, cid_names in zip(projetos_criados, regioes_aceitas_list, estados_aceitos_list, cidades_aceitas_list):
            regioes_objs = filtrar_objs(todas_regioes, reg_names, ['nome', 'abreviacao'])
            estados_objs = filtrar_objs(todos_estados, est_names, ['nome', 'uf'])
            cidades_objs = filtrar_objs(todas_cidades, cid_names, ['nome', 'estado__regiao__nome', 'estado__regiao__abreviacao'])

            proj.regioes_aceitas.set(regioes_objs)
            proj.estados_aceitos.set(estados_objs)
            proj.cidades_aceitas.set(cidades_objs)

        importacao_obj.linhas_lidas = total_linhas
        importacao_obj.projetos_criados = len(projetos)
        importacao_obj.projetos_ignorados = len(ignoradas)
        importacao_obj.linhas_ignoradas_texto = "\n".join(ignoradas)
        importacao_obj.save()
