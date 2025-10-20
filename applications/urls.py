from django.urls import path
from .views import *

app_name = 'application'

urlpatterns = [
    path('inscrever_se/<uuid:project_id>/', InscreverProjetoView.as_view(), name='enroll_in_project'),
    path('atualizar_inscricao/<uuid:application_id>/', EditarInscricaoView.as_view(), name='update_application'),
    path('<uuid:inscricao_id>/baixar/<str:campo>/', AnexoDownloadView.as_view(), name='baixar_arquivo_inscricao'),
    # path('professora/', inscricao_professora, name='inscricao_professora'),

    path('professora/', inscricao_professora, name='inscricao_professora_default'),
    path('professora/step=<int:step>/', inscricao_professora, name='inscricao_professora'),
   
    path('aluna/', inscricao_aluna, name='inscricao_aluna_default'),
    path('aluna/step=<int:step>/', inscricao_aluna, name='inscricao_aluna'),
    path('alunas/rascunho-indeferida/', AlunasRascunhoIndeferidaListView.as_view(), name='alunas_rascunho_indeferida'),


    path("inscricao/editar/<uuid:inscricao_id>/", editar_inscricao, name="editar_inscricao"),
    path("inscricao/professora/editar/<uuid:inscricao_id>/", inscricao_professora, name="editar_inscricao_professora"),
    path("inscricao/aluna/editar/<uuid:inscricao_id>/", inscricao_aluna, name="editar_inscricao_aluna"),

    path('minhas-inscricoes/', minhas_inscricoes, name='minhas_inscricoes'),

    path('visualizar/<uuid:inscricao_id>/', visualizar_inscricao, name='visualizar_inscricao'),
    path('filtrar-cidade-estado/', filtrar_cidade_estado, name='filtrar_cidade_estado'),
]
