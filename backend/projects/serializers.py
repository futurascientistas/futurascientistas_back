from typing import List, Type
from django.db.models import Q, Model, QuerySet
from rest_framework import serializers
from core.models import Regiao, Estado, Cidade
from .models import Project

class ProjectSerializer(serializers.ModelSerializer):
    regioes_aceitas = serializers.CharField(write_only=True, required=False)
    estados_aceitos = serializers.CharField(write_only=True, required=False)
    cidades_aceitas = serializers.CharField(write_only=True, required=False)

    regioes_aceitas_obj = serializers.PrimaryKeyRelatedField(many=True, read_only=True, source='regioes_aceitas')
    estados_aceitos_obj = serializers.PrimaryKeyRelatedField(many=True, read_only=True, source='estados_aceitos')
    cidades_aceitas_obj = serializers.PrimaryKeyRelatedField(many=True, read_only=True, source='cidades_aceitas')

    class Meta:
        model = Project
        fields = '__all__'

    def validate(self, attrs):
        data_inicio = attrs.get('data_inicio', getattr(self.instance, 'data_inicio', None))
        data_fim = attrs.get('data_fim', getattr(self.instance, 'data_fim', None))

        if data_inicio and data_fim and data_inicio > data_fim:
            raise serializers.ValidationError("A data de início não pode ser maior que a data de fim.")

        return attrs

    def _parse_ids(self, value: str) -> list[int]:
        if not value:
            return []
        return [int(v.strip()) for v in value.split(',') if v.strip().isdigit()]

    def _parse_values(self, value: str) -> List[str]:
        if not value:
            return []
        return [v.strip() for v in value.split(',') if v.strip()]

    def _fetch_related_objs(
        self,
        model: Type[Model],
        values: List[str],
        lookup_fields: List[str]
    ) -> QuerySet:
        if not values:
            return model.objects.none()

        queries = Q()
        for val in values:
            val_queries = Q()
            for field in lookup_fields:
                val_queries |= Q(**{f"{field}__iexact": val})
            queries |= val_queries

        return model.objects.filter(queries).distinct()

    def _handle_m2m_field(
        self,
        instance: Project,
        field_name: str,
        model: Type[Model],
        lookup_fields: List[str],
        data: dict
    ):
        raw_value = data.get(field_name, None)
        if raw_value is None:
            return

        values = self._parse_values(raw_value)
        related_objs = self._fetch_related_objs(model, values, lookup_fields)
        getattr(instance, field_name).set(related_objs)

    def create(self, validated_data):
        m2m_fields = ['regioes_aceitas', 'estados_aceitos', 'cidades_aceitas']
        m2m_data = {field: validated_data.pop(field, None) for field in m2m_fields}

        instance = Project.objects.create(**validated_data)

        if m2m_data['regioes_aceitas']:
            ids = self._parse_ids(m2m_data['regioes_aceitas'])
            instance.regioes_aceitas.set(Regiao.objects.filter(id__in=ids))

        if m2m_data['estados_aceitos']:
            ids = self._parse_ids(m2m_data['estados_aceitos'])
            instance.estados_aceitos.set(Estado.objects.filter(id__in=ids))

        if m2m_data['cidades_aceitas']:
            ids = self._parse_ids(m2m_data['cidades_aceitas'])
            instance.cidades_aceitas.set(Cidade.objects.filter(id__in=ids))

        # self._handle_m2m_field(instance, 'regioes_aceitas', Regiao, ['nome', 'abreviacao'], m2m_data)
        # self._handle_m2m_field(instance, 'estados_aceitos', Estado, ['nome', 'uf'], m2m_data)
        # self._handle_m2m_field(instance, 'cidades_aceitas', Cidade, ['nome', 'regiao__nome', 'regiao__abreviacao'], m2m_data)
        return instance

    def update(self, instance, validated_data):
        m2m_fields = ['regioes_aceitas', 'estados_aceitos', 'cidades_aceitas']
        m2m_data = {field: validated_data.pop(field, None) for field in m2m_fields}

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        self._handle_m2m_field(instance, 'regioes_aceitas', Regiao, ['nome', 'abreviacao'], m2m_data)
        self._handle_m2m_field(instance, 'estados_aceitos', Estado, ['nome', 'uf'], m2m_data)
        self._handle_m2m_field(instance, 'cidades_aceitas', Cidade, ['nome', 'regiao__nome', 'regiao__abreviacao'], m2m_data)

        return instance
