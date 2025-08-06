from django.urls import path
from .views import *

urlpatterns = [
    path('todos/', ProjectListAPIView.as_view(), name='projeto-list'),
    path('criar/', ProjectCreateAPIView.as_view(), name='projeto-criar'),
    path('atualizar/<uuid:pk>/', ProjectUpdateAPIView.as_view(), name='projeto-atualizar'),
    path('apagar/<uuid:pk>/', ProjectDeleteAPIView.as_view(), name='projeto-apagar'),
    path('apagar-multiplos/', ProjectBulkDeleteAPIView.as_view(), name='projeto-remover-multiplos'),
    path('importar-projetos/', ImportarProjetosView.as_view(), name='importar_projetos'),
    path('verificar-inscricao/<uuid:project_id>/', VerificarInscricaoView.as_view(), name='verificar-inscricao'),
    path('projeto/<uuid:id>/', ProjectRetrieveAPIView.as_view(), name='project-detail'),
    path('', lista_projetos, name='lista_projetos'),
    path('projetos/<uuid:projeto_id>/', detalhes_projeto, name='detalhes_projeto'),

]
