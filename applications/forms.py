from django import forms

from utils.utils import get_binary_field_display_name
from .models import *
from projects.models import *
from users.models import *
from core.models import *
from ckeditor.fields import RichTextField
from django.utils import timezone
from django.db.models import Q

#Importações para o Drive:
import os
from .drive.drive_services import DriveService


import logging
import traceback

logger = logging.getLogger(__name__)

class ApplicationAlunoForm(forms.ModelForm):

    DRIVE_UPLOAD_FIELDS = {
        'drive_rg_frente': "RG Frente",
        'drive_rg_verso': "RG Verso", 
        'drive_cpf_anexo': "CPF",
        'drive_declaracao_inclusao': 'Autodeclaração para cotas'
    }

    endereco_fields = ['rua', 'cidade', 'estado', 'cep']

    rua = forms.CharField(label="Rua", required=True)
    numero = forms.CharField(label="Número", required=True)
    estado = forms.ModelChoiceField(
        label="Estado",
        queryset=Estado.objects.all().order_by('nome'),
        empty_label="Selecione um estado",
        required=True,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2'
        })
    )

    cidade = forms.ModelChoiceField(
        label="Cidade",
        queryset=Cidade.objects.all().order_by('nome'),
        empty_label="Selecione uma cidade",
        required=True,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2'
        })
    )
    cep = forms.CharField(label="CEP", required=True)  

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
        label=Application._meta.get_field("necessita_material_especial").verbose_name,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )

    tipo_material_necessario = forms.CharField(
        label=Application._meta.get_field("tipo_material_necessario").verbose_name,
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Ex: Material impresso em braile, Material impresso ampliado'}),
        required=False
    )
    
    tamanho_jaleco = forms.ChoiceField(
        choices=[('', 'Selecione um tamanho')] + list(Application.JALECO_CHOICES),
        label="Selecione um tamanho para o jaleco",
        required=True,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2',
        })
    )

    class Meta:
        model = Application
        fields = [
            'projeto',
            'tipo_de_vaga',
            'tamanho_jaleco',
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
        
    def _upload_documents_to_drive(self, instance, drive_service=None, only_field=None):
        try:
            if not drive_service:
                drive_service = DriveService()

            # Verifica acesso à pasta raiz
            if not drive_service.test_folder_access(settings.DRIVE_ROOT_FOLDER_ID):
                logger.error("Falha ao acessar a pasta raiz. Verifique ID/credenciais.")
                raise forms.ValidationError("Falha no acesso ao Google Drive. Contate o administrador.")

            logger.info("Iniciando upload para o Drive")
            
            # Pasta do projeto
            projeto_folder_id = drive_service.find_or_create_folder(
                folder_name=instance.projeto.nome,
                parent_folder_id=settings.DRIVE_ROOT_FOLDER_ID
            )

            # Pasta do usuário
            user_folder_id = drive_service.find_or_create_folder(
                folder_name=instance.usuario.cpf,
                parent_folder_id=projeto_folder_id
            )

            # Upload de arquivos
            for field_name in self.DRIVE_UPLOAD_FIELDS.keys():
                if only_field and field_name != only_field:
                    continue

                upload_field = f"{field_name}__upload"
                if upload_field in self.files:
                    file = self.files[upload_field]
                    if not file:
                        continue

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

    def _clear_documents_from_drive(self, instance, drive_service=None):

        if not drive_service:
            drive_service = DriveService()
            
        for field_name in self.DRIVE_UPLOAD_FIELDS.keys():
            clear_field = f"{field_name}__clear"
            if self.cleaned_data.get(clear_field):
                file_id = getattr(instance, field_name, None)
                print(f"Campo {field_name} marcado para remoção. ID atual: {file_id}")
                if file_id:
                    try:
                        drive_service.delete_file(file_id)
                        logger.info(f"Arquivo {field_name} removido do Drive (ID: {file_id})")
                    except Exception as e:
                        logger.error(f"Falha ao remover {field_name} do Drive: {str(e)}")
                setattr(instance, field_name, None) 
    
    def save(self, commit=True, auto_upload_field=None):

        instance = self.instance or Application(usuario=self.user)

        if self.user:
            instance.usuario = self.user

        # for field in self.Meta.fields:
        #     if field in self.cleaned_data:
        #         setattr(instance, field, self.cleaned_data[field])

        drive_service = DriveService()

        # Fluxo de auto-upload: salva apenas o campo enviado
        if auto_upload_field:
            model_field_name = auto_upload_field.replace('__upload', '')

            if not getattr(instance, "projeto_id", None) and instance.pk:
                instance.refresh_from_db(fields=["projeto"])

            if not getattr(instance, "projeto_id", None):
                raise forms.ValidationError("Escolha um projeto antes de enviar documentos.")

            # Faz upload apenas do campo enviado
            self._upload_documents_to_drive(instance, drive_service, only_field=model_field_name)
           
            # Salva apenas o campo alterado
            if commit:
                # if instance.pk:
                instance.save(update_fields=[model_field_name])
                # else:
                #     instance.save()
                try:
                    instance.refresh_from_db(fields=[model_field_name])
                except Exception:
                    instance = Application.objects.get(pk=instance.pk)
            
            logger.info(f"[SAVE] {model_field_name} depois do refresh -> {getattr(instance, model_field_name, None)}")

            return instance

        # Campos de arquivos do User -- tem que pegar a lista completa depois
        if self.user:
            for doc_field in ["drive_rg_frente", "drive_rg_verso", "drive_cpf_anexo"]:
                if not getattr(instance, doc_field, None):
                    user_file_id = getattr(self.user, doc_field, None)
                    if user_file_id:
                        setattr(instance, doc_field, user_file_id)

        if not instance.projeto:
            raise forms.ValidationError("Selecione um projeto antes de enviar os documentos.")
    
        self._clear_documents_from_drive(instance, drive_service)
        self._upload_documents_to_drive(instance, drive_service)

        # # Atualiza/Cria endereço do usuário
        # endereco = getattr(instance.usuario, 'endereco', None)
        # if endereco is None:
        #     endereco = Endereco.objects.create(
        #         rua=self.cleaned_data.get('rua'),
        #         numero=self.cleaned_data.get('numero'),
        #         cep=self.cleaned_data.get('cep')
        #     )
        #     instance.usuario.endereco = endereco
        #     instance.usuario.save(update_fields=["endereco"])
        # else:
        #     endereco.rua = self.cleaned_data.get('rua')
        #     endereco.numero = self.cleaned_data.get('numero')
        #     endereco.cep = self.cleaned_data.get('cep')
        #     endereco.save()

        # Salva apenas os campos do step atual
        if commit:
            step_fields = self.step_fields.get(self.current_step, [])
            valid_fields = [f for f in step_fields if f in [fld.name for fld in instance._meta.get_fields()]]
            
            valid_fields += [f for f in self.DRIVE_UPLOAD_FIELDS.keys() if getattr(instance, f)]

            if valid_fields:
                instance.save(update_fields=list(set(valid_fields)))
            else:
                instance.save()

        return instance
    
    def clean_numero_edicoes_participadas(self):
        num = self.cleaned_data.get('numero_edicoes_participadas')
        if num is not None and num < 0:
            raise forms.ValidationError("Número de participações anteriores não pode ser negativo.")
        return num
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.current_step = int(kwargs.pop('current_step', 1))
        self.step_fields = kwargs.pop('step_fields', {})

        super().__init__(*args, **kwargs)

        for field_name, label in self.DRIVE_UPLOAD_FIELDS.items():
            verbose_name = Application._meta.get_field(field_name).verbose_name

            self.fields[f"{field_name}__upload"] = forms.FileField(
                required=False,
                label=f"Enviar {verbose_name}",
                help_text="O arquivo será salvo apenas no Drive"
            )
            self.fields[f"{field_name}__upload"].friendly_label = label 
            self.fields[f"{field_name}__upload"].drive_link = None 

            self.fields[f"{field_name}__clear"] = forms.BooleanField(
                required=False,
                widget=forms.HiddenInput(),
                label=f"Remover {verbose_name} atual do Drive"
            )

            file_id = getattr(self.instance, field_name, None)

            if not file_id and self.user and hasattr(self.user, field_name):
                file_id = getattr(self.user, field_name, None)
                if file_id:
                    setattr(self.instance, field_name, file_id)
                    
            link = ""
            if file_id:
                link = f"https://drive.google.com/file/d/{file_id}/view"
                self.fields[f"{field_name}__upload"].drive_link = link
                self.fields[f"{field_name}__upload"].help_text = (
                    f"Arquivo já enviado: <a href='{link}' target='_blank'>ver no Drive</a>. "
                    "Envie outro para substituir ou clique na lixeira para remover."
                )
            else:
                self.fields[f"{field_name}__upload"].help_text = "Nenhum arquivo enviado ainda."

            self.fields[f"{field_name}__upload"].widget.attrs['data_drive_link'] = link

        # torna todos os campos opcionais de início
        for field in self.fields.values():
            field.required = False

        # marca como obrigatórios apenas os do passo atual
        for field_name in self.step_fields.get(self.current_step, []):
            if field_name.endswith("__upload"):
                model_field = field_name.replace("__upload", "")
                file_saved = getattr(self.instance, model_field, None) or getattr(self.user, model_field, None)
                if not file_saved:
                    self.fields[field_name].required = True
                # if not getattr(self.instance, model_field, None):
                #     self.fields[field_name].required = True
            else:
                if field_name in self.fields:
                    self.fields[field_name].required = True

        # popula os campos com valores iniciais do instance
        for field_name in self.fields:
            if hasattr(self.instance, field_name):
                value = getattr(self.instance, field_name)
                if value is not None:
                    self.fields[field_name].initial = value

        # endereço do usuário
        endereco = getattr(getattr(self.instance, "usuario", None), "endereco", None)
        if not endereco and self.user:
            endereco = getattr(self.user, 'endereco', None)

        if endereco:
            self.fields["rua"].initial = endereco.rua
            self.fields["numero"].initial = endereco.numero
            self.fields["cep"].initial = endereco.cep
            self.fields["estado"].initial = endereco.estado
            self.fields["cidade"].initial = endereco.cidade
        else: # adição
            self.fields["rua"].initial = ""
            self.fields["numero"].initial = ""
            self.fields["cep"].initial = ""
            self.fields["estado"].initial = None
            self.fields["cidade"].initial = None


        # projeto inicial + queryset filtrado
        if self.instance.projeto:
            self.fields["projeto"].initial = self.instance.projeto

        projetos = Project.objects.all()
        if endereco:
            projetos = projetos.filter(
                Q(estados_aceitos=endereco.estado) |
                Q(cidades_aceitas=endereco.cidade) |
                Q(eh_remoto=True)
            ).distinct()
        else:
            projetos = projetos.filter(eh_remoto=True)

        self.fields["projeto"].queryset = projetos

    def clean(self):
        cleaned_data = super().clean()

        # if self.instance.pk:
        #     self.instance.refresh_from_db()

        if self.current_step == 4:
           
            upload_model_fields_in_step = [
                f.replace("__upload", "")
                for f in self.step_fields.get(4, [])
                if f.endswith("__upload")
            ]
            for field_name in upload_model_fields_in_step:
                upload_field = f"{field_name}__upload"
                file_sent = self.files.get(upload_field)
                # file_saved = getattr(self.instance, field_name, None)

                file_saved = getattr(self.instance, field_name, None) or getattr(self.user, field_name, None)
                
                if not file_sent and not file_saved:
                    self.add_error(upload_field, "Este arquivo é obrigatório.")

        return cleaned_data


class ApplicationProfessorForm(forms.ModelForm):

    DRIVE_UPLOAD_FIELDS = {
        'drive_rg_frente': "RG Frente",
        'drive_rg_verso': "RG Verso", 
        'drive_cpf_anexo': "CPF",
        'drive_declaracao_inclusao': 'Autodeclaração para cotas',
        'drive_declaracao_vinculo': 'Declaração de vínculo',
        'drive_documentacao_comprobatoria_lattes' : 'Declaração comprobatória do currículo lattes'
    }

    projeto = forms.ModelChoiceField(
        queryset=Project.objects.none(),  
        label="Projeto",
        empty_label="Selecione um projeto",
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2',
        })
    )
    rua = forms.CharField(label="Rua", required=True)
    numero = forms.CharField(label="Número", required=True)
    estado = forms.ModelChoiceField(
        label="Estado",
        queryset=Estado.objects.all().order_by('nome'),
        empty_label="Selecione um estado",
        required=True,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2'
        })
    )

    cidade = forms.ModelChoiceField(
        label="Cidade",
        queryset=Cidade.objects.all().order_by('nome'),
        empty_label="Selecione uma cidade",
        required=True,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2'
        })
    )
    cep = forms.CharField(label="CEP", required=True)  

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

    tamanho_jaleco = forms.ChoiceField(
        choices=[('', 'Selecione um tamanho')] + list(Application.JALECO_CHOICES),
        label="Selecione um tamanho para o jaleco",
        required=True,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2',
        })
    )

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

    class Meta:
        model = Application
        fields = [
            # --- Dados gerais ---
            'projeto',
            'como_soube_programa',
            'curriculo_lattes_url',
            'tamanho_jaleco',
            'area_atuacao',
            'tipo_de_vaga',
            'tipo_deficiencia',
            'necessita_material_especial',
            'tipo_material_necessario',

            # --- Formação e perfil ---
            'grau_formacao',

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
        

    def _upload_documents_to_drive(self, instance, drive_service=None, only_field=None):
        try:
            if not drive_service:
                drive_service = DriveService()

            # Verifica acesso à pasta raiz
            if not drive_service.test_folder_access(settings.DRIVE_ROOT_FOLDER_ID):
                logger.error("Falha ao acessar a pasta raiz. Verifique ID/credenciais.")
                raise forms.ValidationError("Falha no acesso ao Google Drive. Contate o administrador.")

            logger.info("Iniciando upload para o Drive")
            
            # Pasta do projeto
            projeto_folder_id = drive_service.find_or_create_folder(
                folder_name=instance.projeto.nome,
                parent_folder_id=settings.DRIVE_ROOT_FOLDER_ID
            )

            # Pasta do usuário
            user_folder_id = drive_service.find_or_create_folder(
                folder_name=instance.usuario.cpf,
                parent_folder_id=projeto_folder_id
            )

            # Upload de arquivos
            for field_name in self.DRIVE_UPLOAD_FIELDS.keys():
                if only_field and field_name != only_field:
                    continue

                upload_field = f"{field_name}__upload"
                if upload_field in self.files:
                    file = self.files[upload_field]
                    if not file:
                        continue

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

    def _clear_documents_from_drive(self, instance, drive_service=None):

        if not drive_service:
            drive_service = DriveService()
            
        for field_name in self.DRIVE_UPLOAD_FIELDS.keys():
            clear_field = f"{field_name}__clear"
            if self.cleaned_data.get(clear_field):
                file_id = getattr(instance, field_name, None)
                print(f"Campo {field_name} marcado para remoção. ID atual: {file_id}")
                if file_id:
                    try:
                        drive_service.delete_file(file_id)
                        logger.info(f"Arquivo {field_name} removido do Drive (ID: {file_id})")
                    except Exception as e:
                        logger.error(f"Falha ao remover {field_name} do Drive: {str(e)}")
                setattr(instance, field_name, None) 
    
    def save(self, commit=True, auto_upload_field=None):

        instance = self.instance or Application(usuario=self.user)

        if self.user:
            instance.usuario = self.user

        # for field in self.Meta.fields:
        #     if field in self.cleaned_data:
        #         setattr(instance, field, self.cleaned_data[field])

        drive_service = DriveService()

        # Fluxo de auto-upload: salva apenas o campo enviado
        if auto_upload_field:
            model_field_name = auto_upload_field.replace('__upload', '')

            if not getattr(instance, "projeto_id", None) and instance.pk:
                instance.refresh_from_db(fields=["projeto"])

            if not getattr(instance, "projeto_id", None):
                raise forms.ValidationError("Escolha um projeto antes de enviar documentos.")

            # Faz upload apenas do campo enviado
            self._upload_documents_to_drive(instance, drive_service, only_field=model_field_name)
           
            # Salva apenas o campo alterado
            if commit:
                # if instance.pk:
                instance.save(update_fields=[model_field_name])
                # else:
                #     instance.save()
                try:
                    instance.refresh_from_db(fields=[model_field_name])
                except Exception:
                    instance = Application.objects.get(pk=instance.pk)
            
            logger.info(f"[SAVE] {model_field_name} depois do refresh -> {getattr(instance, model_field_name, None)}")

            return instance

        # Campos de arquivos do User -- tem que pegar a lista completa depois
        if self.user:
            for doc_field in ["drive_rg_frente", "drive_rg_verso", "drive_cpf_anexo"]:
                if not getattr(instance, doc_field, None):
                    user_file_id = getattr(self.user, doc_field, None)
                    if user_file_id:
                        setattr(instance, doc_field, user_file_id)

        if not instance.projeto:
            raise forms.ValidationError("Selecione um projeto antes de enviar os documentos.")
    
        self._clear_documents_from_drive(instance, drive_service)
        self._upload_documents_to_drive(instance, drive_service)

        # # Atualiza/Cria endereço do usuário
        # endereco = getattr(instance.usuario, 'endereco', None)
        # if endereco is None:
        #     endereco = Endereco.objects.create(
        #         rua=self.cleaned_data.get('rua'),
        #         numero=self.cleaned_data.get('numero'),
        #         cep=self.cleaned_data.get('cep')
        #     )
        #     instance.usuario.endereco = endereco
        #     instance.usuario.save(update_fields=["endereco"])
        # else:
        #     endereco.rua = self.cleaned_data.get('rua')
        #     endereco.numero = self.cleaned_data.get('numero')
        #     endereco.cep = self.cleaned_data.get('cep')
        #     endereco.save()

        # Salva apenas os campos do step atual
        if commit:
            step_fields = self.step_fields.get(self.current_step, [])
            valid_fields = [f for f in step_fields if f in [fld.name for fld in instance._meta.get_fields()]]
            
            valid_fields += [f for f in self.DRIVE_UPLOAD_FIELDS.keys() if getattr(instance, f)]

            if valid_fields:
                instance.save(update_fields=list(set(valid_fields)))
            else:
                instance.save()

        return instance
    
    def clean_numero_edicoes_participadas(self):
        num = self.cleaned_data.get('numero_edicoes_participadas')
        if num is not None and num < 0:
            raise forms.ValidationError("Número de participações anteriores não pode ser negativo.")
        return num
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.current_step = int(kwargs.pop('current_step', 1))
        self.step_fields = kwargs.pop('step_fields', {})

        super().__init__(*args, **kwargs)

        for field_name, label in self.DRIVE_UPLOAD_FIELDS.items():
            verbose_name = Application._meta.get_field(field_name).verbose_name

            self.fields[f"{field_name}__upload"] = forms.FileField(
                required=False,
                label=f"Enviar {verbose_name}",
                help_text="O arquivo será salvo apenas no Drive"
            )
            self.fields[f"{field_name}__upload"].friendly_label = label 
            self.fields[f"{field_name}__upload"].drive_link = None 

            self.fields[f"{field_name}__clear"] = forms.BooleanField(
                required=False,
                widget=forms.HiddenInput(),
                label=f"Remover {verbose_name} atual do Drive"
            )

            file_id = getattr(self.instance, field_name, None)

            if not file_id and self.user and hasattr(self.user, field_name):
                file_id = getattr(self.user, field_name, None)
                if file_id:
                    setattr(self.instance, field_name, file_id)
                    
            link = ""
            if file_id:
                link = f"https://drive.google.com/file/d/{file_id}/view"
                self.fields[f"{field_name}__upload"].drive_link = link
                self.fields[f"{field_name}__upload"].help_text = (
                    f"Arquivo já enviado: <a href='{link}' target='_blank'>ver no Drive</a>. "
                    "Envie outro para substituir ou clique na lixeira para remover."
                )
            else:
                self.fields[f"{field_name}__upload"].help_text = "Nenhum arquivo enviado ainda."

            self.fields[f"{field_name}__upload"].widget.attrs['data_drive_link'] = link

        # torna todos os campos opcionais de início
        for field in self.fields.values():
            field.required = False

        # marca como obrigatórios apenas os do passo atual
        for field_name in self.step_fields.get(self.current_step, []):
            if field_name.endswith("__upload"):
                model_field = field_name.replace("__upload", "")
                file_saved = getattr(self.instance, model_field, None) or getattr(self.user, model_field, None)
                if not file_saved:
                    self.fields[field_name].required = True
                # if not getattr(self.instance, model_field, None):
                #     self.fields[field_name].required = True
            else:
                if field_name in self.fields:
                    self.fields[field_name].required = True

        # popula os campos com valores iniciais do instance
        for field_name in self.fields:
            if hasattr(self.instance, field_name):
                value = getattr(self.instance, field_name)
                if value is not None:
                    self.fields[field_name].initial = value

        # endereço do usuário
        endereco = getattr(getattr(self.instance, "usuario", None), "endereco", None)
        if not endereco and self.user:
            endereco = getattr(self.user, 'endereco', None)

        if endereco:
            self.fields["rua"].initial = endereco.rua
            self.fields["numero"].initial = endereco.numero
            self.fields["cep"].initial = endereco.cep
            self.fields["estado"].initial = endereco.estado
            self.fields["cidade"].initial = endereco.cidade
        else: # adição
            self.fields["rua"].initial = ""
            self.fields["numero"].initial = ""
            self.fields["cep"].initial = ""
            self.fields["estado"].initial = None
            self.fields["cidade"].initial = None

        # projeto inicial + queryset filtrado
        if self.instance.projeto:
            self.fields["projeto"].initial = self.instance.projeto

        projetos = Project.objects.all()
        if endereco:
            projetos = projetos.filter(
                Q(estados_aceitos=endereco.estado) |
                Q(cidades_aceitas=endereco.cidade) |
                Q(eh_remoto=True)
            ).distinct()
        else:
            projetos = projetos.filter(eh_remoto=True)

        self.fields["projeto"].queryset = projetos

    def clean(self):
        cleaned_data = super().clean()

        # if self.instance.pk:
        #     self.instance.refresh_from_db()

        if self.current_step == 4:
           
            upload_model_fields_in_step = [
                f.replace("__upload", "")
                for f in self.step_fields.get(4, [])
                if f.endswith("__upload")
            ]
            for field_name in upload_model_fields_in_step:
                upload_field = f"{field_name}__upload"
                file_sent = self.files.get(upload_field)
                # file_saved = getattr(self.instance, field_name, None)

                file_saved = getattr(self.instance, field_name, None) or getattr(self.user, field_name, None)
                
                if not file_sent and not file_saved:
                    self.add_error(upload_field, "Este arquivo é obrigatório.")

        return cleaned_data


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['comentario']