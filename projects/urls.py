from django.urls import path
from .views import ProjectCreateAPIView, ProjectListAPIView, ProjectUpdateAPIView, ProjectToggleStatusAPIView

urlpatterns = [
    path('projetos/', ProjectCreateAPIView.as_view(), name='projeto-list'),
    path('projetos/criar/', ProjectListAPIView.as_view(), name='projeto-create'),
    path('projetos/atualizar/<int:pk>/', ProjectUpdateAPIView.as_view(), name='projeto-update'),
    path('projetos/toggle-status/<int:pk>/', ProjectToggleStatusAPIView.as_view(), name='projeto-toggle-status'),
]
