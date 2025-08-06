import django_filters
from django_filters import rest_framework as filters
from .models import Project, FORMATOS, STATUS_PROJETO
from core.models import Regiao, Estado, Cidade
from django.contrib.auth import get_user_model
from django.db.models import Q
from functools import reduce
from operator import or_


User = get_user_model()

class BaseInFilter(django_filters.BaseInFilter):
    fields = []

    def filter(self, qs, value):
        if not value:
            return qs

        if isinstance(value, str):
            values = [v.strip() for v in value.split(',')]
        else:
            values = value

        queries = []
        for val in values:
            queries.append(
                reduce(or_, (Q(**{f"{self.field_name}__{field}__iexact": val}) for field in self.fields))
            )
        q = reduce(or_, queries) if queries else Q()

        return qs.filter(q).distinct()


class RegiaoFilter(BaseInFilter):
    field_name = 'regioes_aceitas'
    fields = ['nome', 'abreviacao']

class CidadeFilter(BaseInFilter):
    field_name = 'cidades_aceitas'
    fields = ['nome', 'regiao__nome', 'regiao__abreviacao']

class EstadoFilter(BaseInFilter):
    field_name = 'estados_aceitos'
    fields = ['nome', 'abreviacao']
    
class ProjectFilter(django_filters.FilterSet):
    nome = filters.CharFilter(lookup_expr='icontains')
    descricao = filters.CharFilter(lookup_expr='icontains')
    criado_por = filters.CharFilter(lookup_expr='icontains')
    atualizado_por = filters.CharFilter(lookup_expr='icontains')

    tutora = filters.ModelChoiceFilter(queryset=User.objects.all())

    eh_remoto = filters.BooleanFilter()
    
    regioes_aceitas = RegiaoFilter(field_name='regioes_aceitas')
    estados_aceitos = EstadoFilter(field_name='estados_aceitos')
    cidades_aceitas = CidadeFilter(field_name='cidades_aceitas')

    formato = filters.ChoiceFilter(choices=FORMATOS)
    status = filters.ChoiceFilter(choices=STATUS_PROJETO)

    data_inicio = django_filters.DateFilter(field_name='data_inicio', lookup_expr='gte')
    data_fim = django_filters.DateFilter(field_name='data_fim', lookup_expr='lte')

    vagas = django_filters.NumberFilter()

    criado_em = django_filters.DateFilter(field_name='criado_em', lookup_expr='gte')
    atualizado_em = django_filters.DateFilter(field_name='atualizado_em', lookup_expr='lte')
    
    class Meta:
        model = Project
        fields = [
            'nome',
            'descricao',
            'criado_por',
            'atualizado_por',
            'tutora',
            'eh_remoto',
            'regioes_aceitas',
            'formato',
            'status',
            'data_inicio',
            'data_fim',
            'vagas',
            'ativo',
            'criado_em',
            'atualizado_em',
        ]
