from rest_framework import serializers
from .models import Regiao, Estado, Cidade, Instituicao
from users.models import Genero, Raca, Deficiencia

class RegiaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Regiao
        fields = '__all__'

class CidadeBulkSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        cidades = []
        erros = []

        for item in validated_data:
            estado_nome = item.pop('estado_nome')
            try:
                estado = Estado.objects.get(nome__iexact=estado_nome)
                cidade = Cidade(estado=estado, **item)
                cidades.append(cidade)
            except Estado.DoesNotExist:
                erros.append(f"Estado '{estado_nome}' não encontrado para cidade '{item.get('nome')}'.")

        if erros:
            raise serializers.ValidationError({"erros": erros})

        return Cidade.objects.bulk_create(cidades, ignore_conflicts=True)
    
class EstadoSerializer(serializers.ModelSerializer):
    regiao_nome = serializers.CharField(write_only=True)
    regiao = RegiaoSerializer(read_only=True)

    class Meta:
        model = Estado
        fields = ['id', 'nome', 'uf', 'regiao', 'regiao_nome']

    def create(self, validated_data):
        regiao_nome = validated_data.pop('regiao_nome')
        try:
            regiao = Regiao.objects.get(nome__iexact=regiao_nome)
        except Regiao.DoesNotExist:
            raise serializers.ValidationError(f"Região '{regiao_nome}' não encontrada.")
        return Estado.objects.create(regiao=regiao, **validated_data)


class CidadeSerializer(serializers.ModelSerializer):
    estado_nome = serializers.CharField(write_only=True)
    estado = EstadoSerializer(read_only=True)

    class Meta:
        model = Cidade
        fields = ['id', 'nome', 'estado', 'estado_nome']
        list_serializer_class = CidadeBulkSerializer

    def create(self, validated_data):
        estado_nome = validated_data.pop('estado_nome')
        try:
            estado = Estado.objects.get(nome__iexact=estado_nome)
        except Estado.DoesNotExist:
            raise serializers.ValidationError(f"Estado '{estado_nome}' não encontrado.")
        return Cidade.objects.create(estado=estado, **validated_data)


class InstituicaoSerializer(serializers.ModelSerializer):
    cidade_nome = serializers.CharField(write_only=True)
    cidade = CidadeSerializer(read_only=True)

    class Meta:
        model = Instituicao
        fields = [
            'id', 'nome', 'telefone', 'email', 'bairro', 'rua', 'numero',
            'complemento', 'cep', 'cidade', 'cidade_nome'
        ]

    def create(self, validated_data):
        cidade_nome = validated_data.pop('cidade_nome')
        try:
            cidade = Cidade.objects.get(nome__iexact=cidade_nome)
        except Cidade.DoesNotExist:
            raise serializers.ValidationError(f"Cidade '{cidade_nome}' não encontrada.")
        return Instituicao.objects.create(cidade=cidade, **validated_data)

class RacaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Raca
        fields = ['id', 'nome']

class GeneroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genero
        fields = ['id', 'nome']

class DeficienciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deficiencia
        fields = ['id', 'nome']