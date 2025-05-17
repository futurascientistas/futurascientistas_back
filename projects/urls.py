from django.urls import path
from .views import ProjectCreateAPIView, ProjectListAPIView, ProjectUpdateAPIView, ProjectDeleteAPIView, ProjectBulkDeleteAPIView

urlpatterns = [
    path('todos/', ProjectListAPIView.as_view(), name='projeto-list'),
    path('criar/', ProjectCreateAPIView.as_view(), name='projeto-criar'),
    path('atualizar/<int:pk>/', ProjectUpdateAPIView.as_view(), name='projeto-atualizar'),
    path('apagar/<int:pk>/', ProjectDeleteAPIView.as_view(), name='projeto-apagar'),
    path('apagar-multiplos/', ProjectBulkDeleteAPIView.as_view(), name='projeto-remover-multiplos'),

]
