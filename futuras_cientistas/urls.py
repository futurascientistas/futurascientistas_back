
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('users.urls')),
    path('projetos/', include('projects.urls')),
    path('inscricoes/', include('applications.urls')),
    path('api/', include('core.urls')),
]

