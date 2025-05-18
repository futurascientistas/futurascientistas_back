from rest_framework import serializers
from .models import Application
from django.utils import timezone

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ['id', 'projeto', 'criado_em', 'usuario']

    def validate(self, data):
        projeto = data.get('projeto')
        now = timezone.now()
        if projeto and not (projeto.inicio_inscricoes <= now <= projeto.fim_inscricoes):
            raise serializers.ValidationError("Inscrição fora do prazo permitido do projeto.")
        return data
