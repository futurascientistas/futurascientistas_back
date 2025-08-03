
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('users.urls')),
    path('projetos/', include('projects.urls')),


    path(
        "inscricoes/",
        include(("applications.urls", "applications"), namespace="applications"),
    ),

    path('api/', include('core.urls')),
]

