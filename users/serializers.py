# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import Group
from .models import User, Genero, Raca, Deficiencia
from django.contrib.auth.models import Permission
from .services import get_valid_group

class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Group.objects.all(),
        required=False
    )
    user_permissions = serializers.SlugRelatedField(
        many=True,
        slug_field='codename',
        queryset=Permission.objects.all(),
        required=False
    )

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def _handle_file_uploads(self, validated_data):
        file_fields = [
            'documento_cpf',
            'documento_rg',
            'foto',
            'comprovante_residencia',
            'autodeclaracao_racial',
            'comprovante_deficiencia'
        ]
        request = self.context['request']

        tipos_permitidos = [
            'application/pdf',
            'image/jpeg',
            'image/jpg',
            'image/png',
        ]

        for field in file_fields:
            file = request.FILES.get(field)
            if file:
                if file.content_type not in tipos_permitidos:
                    raise serializers.ValidationError({
                        field: f"Tipo de arquivo '{file.content_type}' não permitido. Envie apenas PDF ou imagem (jpg, png)."
                    })
                validated_data[field] = file.read()

        return validated_data


    def create(self, validated_data):
        groups = validated_data.pop('groups', None)
        user_permissions = validated_data.pop('user_permissions', None)
        password = validated_data.pop('password', None)
        deficiencias = validated_data.pop('deficiencias', None)

        validated_data = self._handle_file_uploads(validated_data)

        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()

        grupo_final = get_valid_group(groups)
        user.groups.set([grupo_final])

        if user_permissions is not None:
            user.user_permissions.set(user_permissions)

        if deficiencias is not None:
            user.deficiencias.set(deficiencias)

        return user

    def update(self, instance, validated_data):
        groups = validated_data.pop('groups', None)
        user_permissions = validated_data.pop('user_permissions', None)
        password = validated_data.pop('password', None)

        validated_data = self._handle_file_uploads(validated_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        if groups is not None:
            instance.groups.set(groups)

        if user_permissions is not None:
            instance.user_permissions.set(user_permissions)

        return instance

    
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