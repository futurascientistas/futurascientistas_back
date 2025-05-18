from rest_framework import generics, permissions, mixins, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from .models import Project
from .filters import ProjectFilter
from .serializers import ProjectSerializer

class ProjectCreateAPIView(generics.CreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(criado_por=self.request.user.nome + " (" + self.request.user.email + ")")


class ProjectListAPIView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProjectFilter

    def get_queryset(self):
        user = self.request.user
        queryset = Project.objects.all()
        
        if not user.is_staff:
            queryset = queryset.filter(ativo=True)

        return queryset

class ProjectUpdateAPIView(generics.UpdateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_update(self, serializer):
        serializer.save(atualizado_por= self.request.user.nome + " (" + self.request.user.email + ")")

class ProjectDeleteAPIView(generics.DestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAdminUser]

class ProjectBulkDeleteAPIView(mixins.DestroyModelMixin, generics.GenericAPIView):
    queryset = Project.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, *args, **kwargs):
        ids = request.data.get('ids', [])
        if not isinstance(ids, list):
            return Response({"error": "ids precisa ser uma lista"}, status=status.HTTP_400_BAD_REQUEST)

        projects = self.get_queryset().filter(id__in=ids)
        count = projects.count()
        projects.delete()
        return Response({"message": f"{count} projetos deletados."}, status=status.HTTP_200_OK)