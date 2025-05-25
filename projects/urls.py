from django.urls import path
from .views import ProjectCreateAPIView, ProjectListAPIView, ProjectUpdateAPIView, ProjectDeleteAPIView, ProjectBulkDeleteAPIView,ImportarProjetosView, VerificarInscricaoView

urlpatterns = [
    path('todos/', ProjectListAPIView.as_view(), name='projeto-list'),
    path('criar/', ProjectCreateAPIView.as_view(), name='projeto-criar'),
    path('atualizar/<uuid:pk>/', ProjectUpdateAPIView.as_view(), name='projeto-atualizar'),
    path('apagar/<uuid:pk>/', ProjectDeleteAPIView.as_view(), name='projeto-apagar'),
    path('apagar-multiplos/', ProjectBulkDeleteAPIView.as_view(), name='projeto-remover-multiplos'),
    path('importar-projetos/', ImportarProjetosView.as_view(), name='importar_projetos'),
     path('verificar-inscricao/<uuid:project_id>/', VerificarInscricaoView.as_view(), name='verificar-inscricao'),

]
