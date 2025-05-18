from django.urls import path
from .views import InscreverProjetoView

app_name = 'application'

urlpatterns = [
    path('inscrever_se/<uuid:project_id>/', InscreverProjetoView.as_view(), name='enroll_in_project'),
    
]