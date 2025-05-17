from rest_framework import generics, permissions, mixins, status
from rest_framework.response import Response
from .models import Project
from .serializers import ProjectSerializer

class ProjectCreateAPIView(generics.CreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        serializer.save(criado_por=self.request.user)


class ProjectListAPIView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        status_filter = self.request.query_params.get('status')

        if not user.is_staff:
            queryset = Project.objects.filter(ativo=True)
        else:
            queryset = Project.objects.all()
            if status_filter:
                if status_filter.lower() == 'active':
                    queryset = queryset.filter(ativo=True)
                elif status_filter.lower() == 'inactive':
                    queryset = queryset.filter(ativo=False)
        return queryset


class ProjectUpdateAPIView(generics.UpdateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_update(self, serializer):
        serializer.save(atualizado_por=self.request.user)

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