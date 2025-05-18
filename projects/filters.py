import django_filters
from django_filters import rest_framework as filters
from .models import Project, REGIOES_BRASIL, FORMATOS, STATUS_PROJETO
from django.contrib.auth import get_user_model

User = get_user_model()

class ProjectFilter(django_filters.FilterSet):
    nome = filters.CharFilter(lookup_expr='icontains')
    descricao = filters.CharFilter(lookup_expr='icontains')
    criado_por = filters.CharFilter(lookup_expr='icontains')
    atualizado_por = filters.CharFilter(lookup_expr='icontains')

    tutora = filters.ModelChoiceFilter(queryset=User.objects.all())

    eh_remoto = filters.BooleanFilter()
    regioes_aceitas = django_filters.BaseInFilter(
        field_name='regioes_aceitas',
        lookup_expr='contains'  
    )

    formato = filters.ChoiceFilter(choices=FORMATOS)
    status = filters.ChoiceFilter(choices=STATUS_PROJETO)

    data_inicio = django_filters.DateFilter(field_name='data_inicio', lookup_expr='gte')
    data_fim = django_filters.DateFilter(field_name='data_fim', lookup_expr='lte')

    vagas = django_filters.NumberFilter()
    ativo = filters.BooleanFilter()


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
