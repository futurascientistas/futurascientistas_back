from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Application
from projects.models import Project
from .serializers import ApplicationSerializer


class InscreverProjetoView(generics.CreateAPIView):
    serializer_class = ApplicationSerializer

    def perform_create(self, serializer):
        user = self.request.user
        project_id = self.kwargs.get('project_id')
        projeto = get_object_or_404(Project, pk=project_id)

        now = timezone.now()
        if not (projeto.inicio_inscricoes <= now <= projeto.fim_inscricoes):
            raise ValidationError("Inscrição não permitida: fora do período de inscrição.")

        if Application.objects.filter(usuario=user, projeto=projeto).exists():
            raise ValidationError("Você já está inscrita neste projeto.")

        serializer.save(usuario=user, projeto=projeto)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response({"detail": e.detail if hasattr(e, 'detail') else str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
