from rest_framework import generics, status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.views import APIView
from rest_framework.response import Response
from .permissions import IsAdminOrReadOnly
from django.db import models
from .models import Regiao, Estado, Cidade, Instituicao
from .serializers import RegiaoSerializer, EstadoSerializer, CidadeSerializer, InstituicaoSerializer
from users.serializers import GeneroSerializer, RacaSerializer, DeficienciaSerializer
from users.models import Genero, Raca, Deficiencia
from rest_framework.permissions import IsAuthenticatedOrReadOnly


# REGIAO
class RegiaoListCreateView(generics.ListCreateAPIView):
    queryset = Regiao.objects.all()
    serializer_class = RegiaoSerializer


class RegiaoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Regiao.objects.all()
    serializer_class = RegiaoSerializer


# ESTADO
class EstadoListCreateView(generics.ListCreateAPIView):
    queryset = Estado.objects.all()
    serializer_class = EstadoSerializer


class EstadoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Estado.objects.all()
    serializer_class = EstadoSerializer


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


class CidadeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cidade.objects.all()
    serializer_class = CidadeSerializer



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


class InstituicaoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Instituicao.objects.all()
    serializer_class = InstituicaoSerializer


# GENERO
class GeneroListCreateAPIView(generics.ListCreateAPIView):
    queryset = Genero.objects.all()
    serializer_class = GeneroSerializer



class GeneroRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Genero.objects.all()
    serializer_class = GeneroSerializer



class RacaViewSet(viewsets.ModelViewSet):
    queryset = Raca.objects.all()
    serializer_class = RacaSerializer


class DeficienciaViewSet(viewsets.ModelViewSet):
    queryset = Deficiencia.objects.all()
    serializer_class = DeficienciaSerializer
