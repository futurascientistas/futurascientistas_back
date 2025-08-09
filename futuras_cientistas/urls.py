
from django.contrib import admin
from django.urls import path, include
from core.views import *
from users.views import *

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
]

def custom_404_view(request, exception):
    return render(request, 'components/landing-page/page_404.html', status=404)

handler404 = custom_404_view
