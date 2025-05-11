from django.urls import path
from .views import CadastroAPIView, LoginAPIView, RecuperacaoSenhaAPIView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('cadastro/', CadastroAPIView.as_view(), name='cadastro'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('recuperacao_senha/', RecuperacaoSenhaAPIView.as_view(), name='recuperacao_senha'),
]
