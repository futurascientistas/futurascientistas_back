from django.urls import path
from .views import *

app_name = 'application'

urlpatterns = [
    path('inscrever_se/<uuid:project_id>/', InscreverProjetoView.as_view(), name='enroll_in_project'),
    path('atualizar_inscricao/<uuid:application_id>/', EditarInscricaoView.as_view(), name='update_application'),
    path('<uuid:inscricao_id>/baixar/<str:campo>/', AnexoDownloadView.as_view(), name='baixar_arquivo_inscricao'),


    path("", ApplicationListView.as_view(), name="list"),
    path("novo/", ApplicationCreateView.as_view(), name="create"),
    path("<uuid:pk>/editar/", ApplicationUpdateView.as_view(), name="update"),
    path("<uuid:pk>/", ApplicationDetailView.as_view(), name="detail"),
    path("<uuid:pk>/download/<str:field>/", download_application_file, name="download"),

    
]