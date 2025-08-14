from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from core.views import *
from users.views import *
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('users.urls')),
    path('projetos/', include('projects.urls')),
    path('inscricoes/', include('applications.urls')),
    path('api/', include('core.urls')),
    path('', HomePageView.as_view(), name='homepage'),
    path('cadastro', CadastroView.as_view(), name='cadastro'),
    path('login', login_view, name='login'), 
    path('logout', logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('404/', NaoEcontrada.as_view(), name='nao-encontrado'),

    # Rotas de recuperação de senha
    path(
        'recuperar-senha/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            subject_template_name='registration/password_reset_subject.txt',
            html_email_template_name='registration/password_reset_email.html',
            success_url='/recuperar-senha/enviado/'
        ),
        name='password_reset'
    ),
    path(
        'recuperar-senha/enviado/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    path(
        'recuperar-senha/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
            success_url='/recuperar-senha/concluido/'
        ),
        name='password_reset_confirm'
    ),
    path(
        'recuperar-senha/concluido/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]

def custom_404_view(request, exception):
    return render(request, 'components/landing-page/page_404.html', status=404)

handler404 = 'futuras_cientistas.urls.custom_404_view'
