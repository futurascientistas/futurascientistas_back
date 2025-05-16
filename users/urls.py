from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, CadastroAPIView, LoginAPIView, RecuperacaoSenhaAPIView, UserListView, UserDetailView, UserUpdateView, UserDeleteView
from rest_framework_simplejwt.views import TokenRefreshView



urlpatterns = [
    path('cadastro/', CadastroAPIView.as_view(), name='cadastro'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('recuperacao_senha/', RecuperacaoSenhaAPIView.as_view(), name='recuperacao_senha'),
    path('usuarios/', UserListView.as_view(), name='lista-usuarios'),
    path('usuario/<int:pk>/', UserDetailView.as_view(), name='detalhe-usuario'),
    path('usuario/editar/<int:pk>/', UserUpdateView.as_view(), name='editar-perfil'),
    path('usuario/excluir/', UserDeleteView.as_view(), name='excluir-conta'),
]