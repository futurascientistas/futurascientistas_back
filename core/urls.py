
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegiaoListCreateView, RegiaoRetrieveUpdateDestroyView,
    EstadoListCreateView, EstadoRetrieveUpdateDestroyView,
    CidadeListCreateView, CidadeRetrieveUpdateDestroyView,
    InstituicaoListCreateView, InstituicaoRetrieveUpdateDestroyView,
    CidadeBulkCreateView, EstadosByRegiaoList,
    CidadesByEstadoView, GeneroListCreateAPIView,
    GeneroRetrieveUpdateDestroyAPIView,
    RacaViewSet, DeficienciaViewSet
    )


router = DefaultRouter()
router.register(r'racas', RacaViewSet, basename='raca')
router.register(r'deficiencias', DeficienciaViewSet, basename='deficiencia')

urlpatterns = [
    path('', include(router.urls)),
    # REGIAO
    path('regioes/', RegiaoListCreateView.as_view(), name='regiao-list-create'),
    path('regioes/<int:pk>/', RegiaoRetrieveUpdateDestroyView.as_view(), name='regiao-detail'),
    path('regioes/<str:filtro>/estados/', EstadosByRegiaoList.as_view(), name='estados-by-regiao'),

    # ESTADO
    path('estados/', EstadoListCreateView.as_view(), name='estado-list-create'),
    path('estados/<int:pk>/', EstadoRetrieveUpdateDestroyView.as_view(), name='estado-detail'),
    path('estados/<str:filtro>/cidades/', CidadesByEstadoView.as_view(), name='cidades-por-estado'),


    # CIDADE
    path('cidades/', CidadeListCreateView.as_view(), name='cidade-list-create'),
    path('cidades/<int:pk>/', CidadeRetrieveUpdateDestroyView.as_view(), name='cidade-detail'),
    path('cidades/criar_varios/', CidadeBulkCreateView.as_view(), name='cidades-bulk-create'),

    # INSTITUICAO
    path('instituicoes/', InstituicaoListCreateView.as_view(), name='instituicao-list-create'),
    path('instituicoes/<int:pk>/', InstituicaoRetrieveUpdateDestroyView.as_view(), name='instituicao-detail'),

    # GENERO
    path('generos/', GeneroListCreateAPIView.as_view(), name='genero-list-create'),
    path('generos/<int:pk>/', GeneroRetrieveUpdateDestroyAPIView.as_view(), name='genero-detail'),

]
