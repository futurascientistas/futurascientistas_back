from rest_framework import serializers
from .models import Project

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

    def validate(self, attrs):
        data_inicio = attrs.get('data_inicio', getattr(self.instance, 'data_inicio', None))
        data_fim = attrs.get('data_fim', getattr(self.instance, 'data_fim', None))

        if data_inicio and data_fim and data_inicio > data_fim:
            raise serializers.ValidationError("A data de início não pode ser maior que a data de fim.")

        return attrs

