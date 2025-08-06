from django.urls import path, include
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView



urlpatterns = [

    # Autenticação
    # path('auth/cadastro/', CadastroAPIView.as_view(), name='cadastro'),
    # path('auth/login/', LoginAPIView.as_view(), name='login'),
    path('dashboard/perfil/', perfil_view, name='perfil'),
    path('auth/cadastro1/', CadastroAPIView.as_view(), name='cadastro'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/recuperacao_senha/', RecuperacaoSenhaAPIView.as_view(), name='recuperacao_senha'),

    # Conta do usuário autenticado (usuário logado)
    path('eu/', GetMyUserView.as_view(), name='meu-usuario'),
    path('eu/editar/', UpdateMyUserView.as_view(), name='editar-meu-usuario'),
    path('excluir/', UserDeleteView.as_view(), name='excluir-conta'),


    # Gerenciamento de usuários (admin ou lista geral)
    path('todos/', UserListView.as_view(), name='lista-usuarios'),
    path('<uuid:pk>/', UserDetailView.as_view(), name='detalhe-usuario'),
    path('editar/<uuid:pk>/', UserUpdateView.as_view(), name='editar-perfil'),

    # Grupos
    path('grupos/<str:group_name>/membros/', GroupMembersAPIView.as_view(), name='grupo-membros'),
    path('grupos/gerenciar/', GerenciarGrupoAPIView.as_view(), name='gerenciar-grupo'),

    # Anexos de user
    path('<uuid:user_id>/anexo/<str:field_name>/', AnexoDownloadView.as_view()),



]
