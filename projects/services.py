from django.utils import timezone
from django.db import transaction
from .models import Project
import pandas as pd
import math
import numpy as np

def parse_regioes_aceitas(valor):
    if not valor or (isinstance(valor, float) and math.isnan(valor)) or str(valor).strip() == '':
        return []
    itens = [regiao.strip() for regiao in str(valor).split(',')]
    return [item for item in itens if item and item.lower() != 'nan']

def preprocess_dataframe(caminho_arquivo):
    df = pd.read_excel(caminho_arquivo)
    df.columns = df.columns.str.strip()
    return df

def parse_linha_para_dados(row, campos_validos, campos_datetime):
    dados = {}
    for col in row.index:
        if col not in campos_validos or col == 'regioes_aceitas':
            continue
        valor = row[col]

        if pd.isna(valor) or valor == np.nan:
            dados[col] = None
            continue

        if col in campos_datetime and timezone.is_naive(valor):
            valor = timezone.make_aware(valor, timezone.get_current_timezone())

        dados[col] = valor

    dados['regioes_aceitas'] = parse_regioes_aceitas(row.get('regioes_aceitas'))
    return dados

def criar_projeto_com_validacao(dados):
    projeto = Project(**dados)
    projeto.full_clean()
    return projeto

def importar_planilha_projetos(importacao_obj):
    df = preprocess_dataframe(importacao_obj.arquivo.path)
    campos_validos = [f.name for f in Project._meta.get_fields()]
    campos_datetime = ['data_inicio', 'data_fim', 'inicio_inscricoes', 'fim_inscricoes']

    projetos = []
    ignoradas = []
    total_linhas = len(df)

    for index, row in df.iterrows():
        try:
            dados = parse_linha_para_dados(row, campos_validos, campos_datetime)
            projeto = criar_projeto_com_validacao(dados)
            projetos.append(projeto)
        except Exception as e:
            ignoradas.append(
                f"Linha {index + 2} - não processada\n"
                f"    Conteúdo: {dados}\n"
                f"    Motivo: {str(e)}\n"
            )

    with transaction.atomic():
        Project.objects.bulk_create(projetos)
        importacao_obj.linhas_lidas = total_linhas
        importacao_obj.projetos_criados = len(projetos)
        importacao_obj.projetos_ignorados = len(ignoradas)
        importacao_obj.linhas_ignoradas_texto = "\n".join(ignoradas)
        importacao_obj.save()
