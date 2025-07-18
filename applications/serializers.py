from rest_framework import serializers
from .models import Application
from projects.models import Project
from django.utils import timezone

class ApplicationSerializer(serializers.ModelSerializer):
    documento_cpf_upload = serializers.FileField(write_only=True, required=False)
    documento_rg_upload = serializers.FileField(write_only=True, required=False)
    foto_upload = serializers.FileField(write_only=True, required=False)
    comprovante_residencia_upload = serializers.FileField(write_only=True, required=False)
    autodeclaracao_racial_upload = serializers.FileField(write_only=True, required=False)
    laudo_medico_deficiencia_upload = serializers.FileField(write_only=True, required=False)
    boletim_escolar_upload = serializers.FileField(write_only=True, required=False)
    termo_autorizacao_upload = serializers.FileField(write_only=True, required=False)
    rg_frente_upload = serializers.FileField(write_only=True, required=False)
    rg_verso_upload = serializers.FileField(write_only=True, required=False)
    cpf_anexo_upload = serializers.FileField(write_only=True, required=False)
    declaracao_vinculo_upload = serializers.FileField(write_only=True, required=False)
    documentacao_comprobatoria_lattes_upload = serializers.FileField(write_only=True, required=False)
    
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

    def _handle_file_upload(self, instance, validated_data, upload_field, model_field):
        file = validated_data.pop(upload_field, None)
        if file:
            content_type = file.content_type
            allowed_types = [
                'application/pdf',
                'image/jpeg',
                'image/png',
                'image/jpg'
            ]
            if content_type not in allowed_types:
                raise serializers.ValidationError(f"Arquivo {upload_field} deve ser PDF ou imagem.")
            setattr(instance, model_field, file.read())

    def create(self, validated_data):
        instance = Application()
        for upload_field, model_field in [
            ('documento_cpf_upload', 'documento_cpf'),
            ('documento_rg_upload', 'documento_rg'),
            ('foto_upload', 'foto'),
            ('comprovante_residencia_upload', 'comprovante_residencia'),
            ('autodeclaracao_racial_upload', 'autodeclaracao_racial'),
            ('laudo_medico_deficiencia_upload', 'laudo_medico_deficiencia'),
            ('boletim_escolar_upload', 'boletim_escolar'),
            ('termo_autorizacao_upload', 'termo_autorizacao'),
            ('rg_frente_upload', 'rg_frente'),
            ('rg_verso_upload', 'rg_verso'),
            ('cpf_anexo_upload', 'cpf_anexo'),
            ('declaracao_vinculo_upload', 'declaracao_vinculo'),
            ('documentacao_comprobatoria_lattes_upload', 'documentacao_comprobatoria_lattes'),
        ]:
            self._handle_file_upload(instance, validated_data, upload_field, model_field)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def update(self, instance, validated_data):
        for upload_field, model_field in [
            ('documento_cpf_upload', 'documento_cpf'),
            ('documento_rg_upload', 'documento_rg'),
            ('foto_upload', 'foto'),
            ('comprovante_residencia_upload', 'comprovante_residencia'),
            ('autodeclaracao_racial_upload', 'autodeclaracao_racial'),
            ('laudo_medico_deficiencia_upload', 'laudo_medico_deficiencia'),
            ('boletim_escolar_upload', 'boletim_escolar'),
            ('termo_autorizacao_upload', 'termo_autorizacao'),
            ('rg_frente_upload', 'rg_frente'),
            ('rg_verso_upload', 'rg_verso'),
            ('cpf_anexo_upload', 'cpf_anexo'),
            ('declaracao_vinculo_upload', 'declaracao_vinculo'),
            ('documentacao_comprobatoria_lattes_upload', 'documentacao_comprobatoria_lattes'),
        ]:
            self._handle_file_upload(instance, validated_data, upload_field, model_field)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class ProjectWithApplicationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'id', 'nome', 'data_resultado_homologacao',
            'inicio_inscricoes', 'fim_inscricoes', 'status'
        ]
    
    inscricoes_aprovadas = serializers.SerializerMethodField()
    
    def get_inscricoes_aprovadas(self, obj):
        return Application.objects.filter(
            projeto=obj,
            aprovado=True
        ).count()