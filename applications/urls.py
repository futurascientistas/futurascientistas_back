from django.urls import path
from .views import *

app_name = 'application'

urlpatterns = [
    path('inscrever_se/<uuid:project_id>/', InscreverProjetoView.as_view(), name='enroll_in_project'),
    path('atualizar_inscricao/<uuid:application_id>/', EditarInscricaoView.as_view(), name='update_application'),
    
]