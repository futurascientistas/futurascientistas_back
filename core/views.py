from rest_framework import generics, status, viewsets, mixins
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.response import Response

from users.models.school_transcript_model import Disciplina
from .permissions import IsAdminOrReadOnly
from django.db import models
from django.shortcuts import render
from .models import Regiao, Estado, Cidade, Instituicao
from .serializers import RegiaoSerializer, EstadoSerializer, CidadeSerializer, InstituicaoSerializer
from users.serializers import DisciplinaSerializer, GeneroSerializer, RacaSerializer, DeficienciaSerializer, TipoDeVagaSerializer, TipoEnsinoSerializer
from users.models import Genero, Raca, Deficiencia, TipoDeVaga, TipoEnsino
from django.views.generic import TemplateView
from rest_framework.permissions import IsAuthenticatedOrReadOnly


# REGIAO
class RegiaoListCreateView(generics.ListCreateAPIView):
    queryset = Regiao.objects.all()
    serializer_class = RegiaoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class RegiaoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Regiao.objects.all()
    serializer_class = RegiaoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

# ESTADO
class EstadoListCreateView(generics.ListCreateAPIView):
    queryset = Estado.objects.all()
    serializer_class = EstadoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class EstadoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Estado.objects.all()
    serializer_class = EstadoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class EstadosByRegiaoList(generics.ListAPIView):
    serializer_class = EstadoSerializer

    def get_queryset(self):
        filtro = self.kwargs['filtro']
        query = models.Q(nome__iexact=filtro) | models.Q(abreviacao__iexact=filtro)

        if filtro.isdigit():
            query |= models.Q(pk=int(filtro))

        try:
            regiao = Regiao.objects.get(query)
        except Regiao.DoesNotExist:
            raise NotFound("Região não encontrada.")

        return Estado.objects.filter(regiao=regiao)


# CIDADE
class CidadeListCreateView(generics.ListCreateAPIView):
    queryset = Cidade.objects.all()
    serializer_class = CidadeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class CidadeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cidade.objects.all()
    serializer_class = CidadeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CidadesByEstadoView(generics.ListAPIView):
    serializer_class = CidadeSerializer

    def get_queryset(self):
        filtro = self.kwargs['filtro']
        try:
            query = models.Q(uf__iexact=filtro) | models.Q(nome__iexact=filtro)
            if filtro.isdigit():
                query |= models.Q(pk=int(filtro))
            estado = Estado.objects.get(query)
        except Estado.DoesNotExist:
            raise NotFound("Estado não encontrado.")
        return Cidade.objects.filter(estado=estado)


class CidadeBulkCreateView(APIView):
    def post(self, request):
        serializer = CidadeSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": f"{len(serializer.validated_data)} cidades criadas."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# INSTITUICAO
class InstituicaoListCreateView(generics.ListCreateAPIView):
    queryset = Instituicao.objects.all()
    serializer_class = InstituicaoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class InstituicaoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Instituicao.objects.all()
    serializer_class = InstituicaoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

# GENERO
class GeneroListCreateAPIView(generics.ListCreateAPIView):
    queryset = Genero.objects.all()
    serializer_class = GeneroSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class GeneroRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Genero.objects.all()
    serializer_class = GeneroSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class RacaViewSet(viewsets.ModelViewSet):
    queryset = Raca.objects.all()
    serializer_class = RacaSerializer
    permission_classes = [IsAdminOrReadOnly]


class DeficienciaViewSet(viewsets.ModelViewSet):
    queryset = Deficiencia.objects.all()
    serializer_class = DeficienciaSerializer
    permission_classes = [IsAdminOrReadOnly]

class TipoDeVagaViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = TipoDeVaga.objects.all()
    serializer_class = TipoDeVagaSerializer
    permission_classes = [IsAdminOrReadOnly]

class DisciplinaViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Disciplina.objects.all()
    serializer_class = DisciplinaSerializer
    permission_classes = [IsAdminOrReadOnly]

class HomePageView(TemplateView):
    template_name = "components/landing-page/home.html"

class TipoEnsinoViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = TipoEnsino.objects.all()
    serializer_class = TipoEnsinoSerializer
    permission_classes = [IsAdminOrReadOnly]

class NaoEcontrada(TemplateView):
    template_name = "components/landing-page/page_404.html"

class ContatosView(TemplateView):
    template_name = "components/landing-page/contact_information.html"

class CronogramaView(TemplateView):
    template_name = "components/agenda/calendar.html"
