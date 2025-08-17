from django import forms

from utils.utils import get_binary_field_display_name
from .models import *
from projects.models import *
from users.models import *
from ckeditor.fields import RichTextField
from django.utils import timezone
from django.db.models import Q

#Importações para o Drive:
import os
from .drive.drive_services import DriveService

from io import BytesIO  # Para BytesIO
from googleapiclient.http import MediaIoBaseUpload 

import logging
import traceback

logger = logging.getLogger(__name__)
class ApplicationAlunoForm(forms.ModelForm):
    # BINARY_FILE_FIELDS = [
    #     'rg_frente',
    #     'rg_verso',
    #     'cpf_anexo',
    #     'declaracao_inclusao'
    # ]
    
    DRIVE_UPLOAD_FIELDS = {
        'drive_rg_frente': "RG Frente",
        'drive_rg_verso': "RG Verso", 
        'drive_cpf_anexo': "CPF"
    }

    projeto = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        label="Projeto",
        empty_label="Selecione um projeto",
        required=True,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2',
        })
    )
    

    

    necessita_material_especial = forms.BooleanField(
        label="Necessita de material especial?",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )

    tipo_material_necessario = forms.CharField(
        label="Indicar o tipo de material necessário",
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Ex: Material impresso em braile, Material impresso ampliado'}),
        required=False
    )

    # for field_name in BINARY_FILE_FIELDS:

    #     display_label = display_label = get_binary_field_display_name(field_name)

    #     locals()[f"{field_name}__upload"] = forms.FileField(
    #         label=f"Enviar arquivo para {display_label}",
    #         required=False,
    #         help_text="Deixe em branco para manter o arquivo atual."
    #     )
    #     locals()[f"{field_name}__clear"] = forms.BooleanField(
    #         label=f"Remover arquivo atual de {display_label}",
    #         required=False
    #     )
    # del field_name
    
    for field_name, label in DRIVE_UPLOAD_FIELDS.items():
        locals()[f"{field_name}__upload"] = forms.FileField(
            required=False,
            label=f"Enviar {label} para o Drive",
            help_text="O arquivo será salvo apenas no Google Drive"
        )
        locals()[f"{field_name}__clear"] = forms.BooleanField(
            required=False,
            label=f"Remover arquivo atual do Drive"
        )
    del field_name, label

    class Meta:
        model = Application
        fields = [
            'projeto',
            'tipo_de_vaga',
            'tipo_deficiencia',
            'necessita_material_especial',
            'tipo_material_necessario',
            'aceite_declaracao_veracidade',
            'aceite_requisitos_tecnicos',
        ]

        widgets = {
            'aceite_declaracao_veracidade': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'aceite_requisitos_tecnicos': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
        
    def _apply_binary_uploads(self, instance):
        for field_name in self.BINARY_FILE_FIELDS:
            upload_field_name = f"{field_name}__upload"
            clear_field_name = f"{field_name}__clear"
            
            if self.cleaned_data.get(clear_field_name):
                setattr(instance, field_name, None)
            
            uploaded_file = self.files.get(upload_field_name)
            if uploaded_file:
                setattr(instance, field_name, uploaded_file.read())

    # def save(self, commit=True):
    #     instance = super().save(commit=False)
    #     # self._apply_binary_uploads(instance)
    #     self._upload_to_drive(instance)
    #     if commit:
    #         instance.save()
    #     return instance
    
    
    

    def _upload_documents_to_drive(self, instance):
        try:
            drive_service = DriveService()
            
            # Verifica acesso antes de criar pasta
            if not drive_service.test_folder_access(settings.DRIVE_ROOT_FOLDER_ID):
                raise Exception("Sem acesso à pasta raiz")
            
            logger.info("Iniciando upload para o Drive")
            
            # Primeiro cria a pasta do projeto (se não existir)
            projeto_folder_name = instance.projeto.nome
            logger.info(f"Verificando/Criando pasta do projeto: {projeto_folder_name}")
            
            projeto_folder_id = drive_service.find_or_create_folder(
                folder_name=projeto_folder_name,
                parent_folder_id=settings.DRIVE_ROOT_FOLDER_ID
            )
            logger.info(f"Pasta do projeto ID: {projeto_folder_id}")
            
            # Depois cria a pasta do usuário (CPF) dentro da pasta do projeto
            user_folder_name = instance.user.cpf
            logger.info(f"Criando pasta do usuário: {user_folder_name}")
            
            user_folder_id = drive_service.create_folder(
                folder_name=user_folder_name,
                parent_folder_id=projeto_folder_id
            )
            logger.info(f"Pasta do usuário criada com ID: {user_folder_id}")

            # Faz upload dos arquivos para a pasta do usuário
            for field_name in ['drive_rg_frente', 'drive_rg_verso', 'drive_cpf_anexo']:
                upload_field = f"{field_name}__upload"
                if upload_field in self.files:
                    file = self.files[upload_field]
                    logger.info(f"Processando arquivo: {file.name}")
                    
                    file_id = drive_service.upload_file(
                        file_name=file.name,
                        file_content=file.read(),
                        mime_type=file.content_type,
                        folder_id=user_folder_id
                    )
                    logger.info(f"Arquivo {file.name} uploadado com ID: {file_id}")
                    setattr(instance, field_name, file_id)
                    
        except Exception as e:
            logger.error(f"Erro completo no upload:\n{traceback.format_exc()}")
            raise forms.ValidationError("Falha temporária no upload de documentos. Por favor, tente novamente mais tarde.")
        
    def save(self, commit=True):
        # Salva os dados do form sem commit primeiro
        instance = super().save(commit=False)

        # Associa o usuário logado ao instance
        if self.user:
            instance.user = self.user

        try:
            # Faz upload para o Drive usando instance.user.cpf
            self._upload_documents_to_drive(instance)
        except forms.ValidationError:
            raise  # Re-lança erros de validação
        except Exception as e:
            logger.error(f"Erro geral no save: {str(e)}")
            if commit:
                instance.save()  # Salva sem os dados do Drive
            raise forms.ValidationError(
                "Ocorreu um erro ao processar seus documentos. "
                "Seu formulário foi salvo, mas você pode precisar reenviar os arquivos."
            )

        if commit:
            instance.save()
        return instance

    def clean(self):
        cleaned_data = super().clean()
        
        if not cleaned_data.get('projeto'):
            self.add_error('projeto', 'O projeto é obrigatório.')
        if not cleaned_data.get('aceite_declaracao_veracidade'):
            self.add_error('aceite_declaracao_veracidade', 'É necessário aceitar a declaração de veracidade.')
        if not cleaned_data.get('aceite_requisitos_tecnicos'):
            self.add_error('aceite_requisitos_tecnicos', 'É necessário aceitar os requisitos técnicos.')
            
        necessita_material = cleaned_data.get('necessita_material_especial')
        tipo_material = cleaned_data.get('tipo_material_necessario')
        
        if necessita_material and not tipo_material:
            self.add_error('tipo_material_necessario', 'Por favor, indique o tipo de material necessário.')

        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        # Pega o usuário logado que foi passado na view
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        hoje = timezone.now().date()
        projetos = Project.objects.all()

        if self.user:
            estado_usuario = getattr(self.user, 'estado', None)
            if estado_usuario and hasattr(estado_usuario, 'id'):
                projetos = projetos.all().distinct()
            else:
                projetos = projetos.all()
        else:
            projetos = Project.objects.none()

        self.fields['projeto'].queryset = projetos



class ApplicationProfessorForm(forms.ModelForm):

    BINARY_FILE_FIELDS = [
        'rg_frente',
        'declaracao_inclusao',
        'rg_verso',
        'cpf_anexo',
        'declaracao_vinculo',
        'documentacao_comprobatoria_lattes',
    ]

    projeto = forms.ModelChoiceField(
        queryset=Project.objects.none(),  
        label="Projeto",
        empty_label="Selecione um projeto",
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2',
        })
    )

    tipo_de_vaga = forms.ModelChoiceField(
        queryset=TipoDeVaga.objects.all(),  
        label="Tipo de Vaga",
        empty_label="Selecione um tipo de vaga",
        required=True,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2',
        })
    )

    grau_formacao = forms.ChoiceField(
        choices=[('', 'Selecione um Grau de Formação')] + list(GrauFormacao.choices),
        label="Grau de formação mais alto",
        required=False,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2',
        })
    )

    # modalidade_vaga = forms.ChoiceField(
    #     choices=[('', 'Selecione uma modalidade')] + list(GrauFormacao.choices),
    #     label="Selecione uma modalidade de vaga",
    #     required=True,
    #     widget=forms.Select(attrs={
    #         'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2',
    #     })
    # )

    tipo_deficiencia = forms.ModelChoiceField(
        queryset=Deficiencia.objects.all(),  
        label="Deficiencia",
        required=True,
        empty_label="Selecione uma deficiencia",
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2',
        })
    )

    CUSTOM_FIELD_LABELS = {
        'rg_frente': 'RG (frente)', 
        'rg_verso': 'RG (verso)',   
        'cpf_anexo': 'CPF',
    }

    for field_name in BINARY_FILE_FIELDS:

        display_label = CUSTOM_FIELD_LABELS.get(field_name, field_name.replace('_', ' ').capitalize())

        locals()[f"{field_name}__upload"] = forms.FileField(
            label=f"Enviar arquivo para {display_label}",
            required=False,
            help_text="Deixe em branco para manter o arquivo atual."
        )
        locals()[f"{field_name}__clear"] = forms.BooleanField(
            label=f"Remover arquivo atual de {display_label}",
            required=False
        )
    del field_name 

    class Meta:
        model = Application
        fields = [
            # --- Dados gerais ---
            'projeto',
            'como_soube_programa',
            'curriculo_lattes_url',
            'area_atuacao',
            'tipo_de_vaga',
            'tipo_deficiencia',
            'necessita_material_especial',
            'tipo_material_necessario',
            'curriculo_lattes_url',

            # --- Formação e perfil ---
            'grau_formacao',
            'perfil_academico',

            # --- Experiência docente ---
            'docencia_superior',
            'docencia_medio',
            'orientacoes_estudantes',
            'participacoes_bancas',

            # --- Produção científica ---
            'periodico_indexado',
            'livro_publicado',
            'capitulo_publicado',
            'anais_congresso',
            'apresentacao_oral',

            # --- Projetos, cursos e eventos ---
            'orientacao_ic',
            'feira_ciencias',
            'curso_extensao',
            'curso_capacitacao',
            'premiacoes',
            'missao_cientifica',

            # --- Projeto submetido ---
            'titulo_projeto_submetido',
            'link_projeto',
            'numero_edicoes_participadas',

            # --- Termos de aceite ---
            'aceite_declaracao_veracidade',
            'aceite_requisitos_tecnicos',
        ]


        widgets = {
            'como_soube_programa': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Como soube do programa?'}),
            'curriculo_lattes_url': forms.URLInput(attrs={'placeholder': 'URL do Currículo Lattes'}),
            'area_atuacao': forms.TextInput(attrs={'placeholder': 'Área de atuação'}),
            'tipo_de_vaga': forms.TextInput(attrs={'placeholder': 'Tipo de Vaga'}),
            'tipo_deficiencia': forms.TextInput(attrs={'placeholder': 'Tipo de deficiência'}),
            'tipo_material_necessario': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Descreva o tipo de material necessário'}),
            'grau_formacao': forms.Select(choices=GrauFormacao.choices),
            'perfil_academico': forms.TextInput(attrs={'placeholder': 'Perfil acadêmico'}),
            'docencia_superior': forms.NumberInput(attrs={'min': 0}),
            'docencia_medio': forms.NumberInput(attrs={'min': 0}),
            'orientacao_ic': forms.NumberInput(attrs={'min': 0}),
            'titulo_projeto_submetido': forms.TextInput(attrs={'placeholder': 'Título do projeto submetido'}),
            'link_projeto': forms.URLInput(attrs={'placeholder': 'Link para o projeto'}),
            'numero_edicoes_participadas': forms.NumberInput(attrs={'min': 0}),
        }
        

    def _apply_binary_uploads(self, instance):
        for field_name in self.BINARY_FILE_FIELDS:
            upload_field = f"{field_name}__upload"
            clear_field = f"{field_name}__clear"
            if self.cleaned_data.get(clear_field):
                setattr(instance, field_name, None)
                continue
            uploaded = self.files.get(upload_field)
            if uploaded:
                setattr(instance, field_name, uploaded.read())

    def save(self, commit=True):
        instance = super().save(commit=False)
        self._apply_binary_uploads(instance)
        if commit:
            instance.save()
            self.save_m2m()
        return instance


    def clean_numero_edicoes_participadas(self):
        num = self.cleaned_data.get('numero_edicoes_participadas')
        if num is not None and num < 0:
            raise forms.ValidationError("Número de edições anteriores não pode ser negativo.")
        return num
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        hoje = timezone.now().date()
        projetos = Project.objects.filter(
            ativo=True,
            #inicio_inscricoes__lte=hoje,
            #fim_inscricoes__gte=hoje,
        )

        if user:
            estado_usuario = getattr(user, 'cidade', None)
            # Verifica se estado_usuario é um objeto válido (não vazio, não string vazia)
            if estado_usuario and hasattr(estado_usuario, 'id'):
                projetos = projetos.filter(
                    Q(cidades_aceitas__isnull=True) | Q(cidades_aceitas=estado_usuario)
                ).distinct()
            else:
                # Se não tem estado válido, só mostra os que não tem estado restrito
                projetos = projetos.filter(cidades_aceitas__isnull=True)

        else:
            projetos = Project.objects.none()

        self.fields['projeto'].queryset = projetos


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['comentario']