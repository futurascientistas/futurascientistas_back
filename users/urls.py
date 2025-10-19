from django.urls import path, include
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView



urlpatterns = [

    # Autenticação
    # path('auth/cadastro/', CadastroAPIView.as_view(), name='cadastro'),
    path('auth/login/', LoginAPIView.as_view(), name='login'),
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
    
    

    
    #API VIEWS
    path('api/alunas-datas/', ApiAlunasDatas.as_view(), name='api-alunas-datas'),
    path('api/professores-datas/', ApiProfessoresDatas.as_view(), name='api-professores-datas'),
    path("api/deficiencia/", ApiUsuariosComDeficiencia.as_view(), name="usuarios-deficiencia"),
    path('api/projetos-em-andamento/', ApiProjetosEmAndamento.as_view(), name='api_projetos_em_andamento'),
    path('api/projetos-concluidos/', ApiPercentualProjetosConcluidos.as_view(), name='api_projetos_concluidos'),
    path('api/projetos-com-regioes/', ApiProjetosComRegioes.as_view(), name='api_projetos_com_regioes'),
    path('api/contagem-tipo-ensino/', ApiContagemPorTipoEnsino.as_view(), name='api_contagem_tipo_ensino'),
    path('api/contagem-cidade/', ApiContagemPorCidade.as_view(), name='api_contagem_cidade'),
    
    
    path('api/dashboard-diversidade/', ApiDashboardDiversidade.as_view(), name='api-dashboard-diversidade'),
    path('api/evolucao-temporal/', ApiEvolucaoTemporal.as_view(), name='api-evolucao-temporal'),
    path('api/funil-performance/', ApiFunilPerformance.as_view(), name='api-funil-performance'),
    path('api/distribuicao-regional/', ApiDistribuicaoRegional.as_view(), name='api-distribuicao-regional'),
    path('api/distribuicao-estados/', ApiDistribuicaoEstados.as_view(), name='api-distribuicao-estados'),    
    path('api/distribuicao-formacao/', ApiDistribuicaoFormacao.as_view(), name='api-distribuicao-formacao'),
    path('api/professoras-distribuicao-regional/', ApiProfessorasDistribuicaoRegional.as_view(), name='professoras-distribuicao-regional'),
    path('api/professoras-distribuicao-tipo-ensino/', ApiProfessorasDistribuicaoTipoEnsino.as_view(), name='professoras-distribuicao-tipo-ensino'),
    path('api/distribuicao-cotas/', ApiDistribuicaoCotas.as_view(), name='api-distribuicao-cotas'),
    path('api/distribuicao-escolas/', ApiDistribuicaoEscolas.as_view(), name='api-distribuicao-escolas'),
    path('api/frequencia-mensal-alunos/', ApiFrequenciaMensalAlunos.as_view(), name='api-frequencia-mensal-alunos'),
    path('api/funil-alunas/', ApiFunilAlunasApplicationLog.as_view(), name='api-funil-alunas'),
    path('api/faixa-etaria/', ApiFaixaEtaria.as_view(), name='api-faixa-etaria'),

    path('dashboardgeral/', Dashboard1.as_view(), name='dashboardgeral'),
    path('dashboardprofessoras/', DashboardProfessoras.as_view(), name='dashboardprofessoras'),
    path('dashalunas/', DashboardAlunas.as_view(), name='dashalunas'),

    #Gerenciamento de usuários e grupos
    path('dashboard/grupos', group_list, name='group_list'),
    path('dashboard/grupos/<int:pk>', group_edit_users, name='group_edit_users'),
    path('api/search-users/', search_users, name='search_users'),


]
