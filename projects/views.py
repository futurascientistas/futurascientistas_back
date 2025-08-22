from rest_framework import generics, permissions, mixins, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.parsers import MultiPartParser
from .models import Project, ImportacaoProjeto
from rest_framework.response import Response
from .serializers import ProjectSerializer
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.shortcuts import get_object_or_404, render, redirect
from .filters import ProjectFilter
from .services import importar_planilha_projetos, registrar_log_status
from django.utils import timezone

class ProjectCreateAPIView(generics.CreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        projeto = serializer.save(criado_por=self.request.user.nome + " (" + self.request.user.email + ")")
       
        registrar_log_status(
            projeto=projeto,
            status_anterior=None,  
            status_novo=projeto.status,
            usuario=self.request.user
        )

class ProjectRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'  

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        if not user.is_staff:
            queryset = queryset.filter(ativo=True)

        return queryset

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
        projeto_antigo = self.get_object()
        status_antigo = projeto_antigo.status

        projeto = serializer.save(atualizado_por=f"{self.request.user.nome} ({self.request.user.email})")
        status_novo = projeto.status

        registrar_log_status(projeto, status_antigo, status_novo, self.request.user)

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
    
class ImportarProjetosView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        arquivo = request.FILES.get('arquivo')
        if not arquivo:
            return Response({"erro": "Arquivo não enviado."}, status=status.HTTP_400_BAD_REQUEST)

        importacao = ImportacaoProjeto.objects.create(arquivo=arquivo)
        try:
            importar_planilha_projetos(importacao, self.request)
        except Exception as e:
            return Response({"erro": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "mensagem": "Importação realizada com sucesso.",
            "linhas_lidas": importacao.linhas_lidas,
            "projetos_criados": importacao.projetos_criados,
            "projetos_ignorados": importacao.projetos_ignorados,
            "linhas_ignoradas": importacao.linhas_ignoradas_texto,
            "id": importacao.id
        })
    
class VerificarInscricaoView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, project_id):
        projeto = get_object_or_404(Project, id=project_id)
        agora = timezone.now()

        pode_inscrever = projeto.inicio_inscricoes <= agora <= projeto.fim_inscricoes
        return Response({"pode_inscrever": pode_inscrever})

def detalhes_projeto(request, projeto_id):
    projeto = get_object_or_404(Project, id=projeto_id)
    return render(request, 'components/projects/detalhes_projeto.html', {'projeto': projeto})


from django.shortcuts import render
from django.shortcuts import render
from .models import Project, Regiao, Estado

def lista_projetos(request):
    queryset = Project.objects.all()

    q = request.GET.get('q', '')
    regiao_id = request.GET.get('regiao', '')
    estado_id = request.GET.get('estado', '')  
    formato = request.GET.get('formato', '')
    ordenar = request.GET.get('ordenar', 'nome')

    if q:
        queryset = queryset.filter(nome__icontains=q)

    if regiao_id:
        queryset = queryset.filter(regioes_aceitas__id=regiao_id)

    if estado_id:
        queryset = queryset.filter(estados_aceitos__id=estado_id) 

    if formato:
        queryset = queryset.filter(formato=formato)

    allowed_order_fields = ['nome', 'data_inicio', 'data_fim', 'vagas']
    if ordenar not in allowed_order_fields:
        ordenar = 'nome'

    queryset = queryset.order_by(ordenar)

    # Paginação
    from django.core.paginator import Paginator
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    projetos_page = paginator.get_page(page_number)

    regioes = Regiao.objects.all()
    estados = Estado.objects.all()  

    return render(request, 'components/projects/lista_projetos.html', {
        'projetos': projetos_page,
        'regioes': regioes,
        'estados': estados,  
        'filtros': {
            'q': q,
            'regiao': regiao_id,
            'estado': estado_id, 
            'formato': formato,
            'ordenar': ordenar,
        }
    })