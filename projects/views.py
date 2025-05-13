from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Project
from rest_framework.permissions import IsAuthenticated
from .serializers import ProjectSerializer

class ProjectCreateAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectListAPIView(APIView):
    permission_classes = [IsAuthenticated]  

    def get(self, request):
        is_admin = request.user.is_staff

        status_filter = request.query_params.get('status', None)

        if not is_admin:
            projects = Project.objects.filter(ativo=True)
        else:
            projects = Project.objects.all()

            if status_filter:
                if status_filter.lower() == 'active':
                    projects = projects.filter(ativo=True)
                elif status_filter.lower() == 'inactive':
                    projects = projects.filter(ativo=False)

        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)


# View para editar um Project
class ProjectUpdateAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def put(self, request, pk):
        try:
            Project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response({'mensagem': 'Project não encontrado'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProjectSerializer(Project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(atualizado_por=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View para desativar/ativar um Project
class ProjectToggleStatusAPIView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, pk):
        try:
            Project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response({'mensagem': 'Project não encontrado'}, status=status.HTTP_404_NOT_FOUND)

        Project.active = not Project.active
        Project.save()
        return Response({'mensagem': 'Status do Project atualizado'}, status=status.HTTP_200_OK)
