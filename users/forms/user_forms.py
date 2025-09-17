import re
from django import forms
from datetime import date
from django.contrib.auth.models import Group
from utils.utils import get_binary_field_display_name
from users.services import validar_email, validar_cpf, validar_senha
from users.models import TipoEnsino
from users.models import Deficiencia, Genero, Raca, User
from django.conf import settings

class CadastroForm(forms.Form):
    nome = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "mt-1 block w-full rounded border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-pink-400 focus:border-pink-400",
            "placeholder": "Nome completo",
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "mt-1 block w-full rounded border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-pink-400 focus:border-pink-400",
            "placeholder": "exemplo@email.com",
        })
    )
    cpf = forms.CharField(
        max_length=14,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "mt-1 block w-full rounded border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-pink-400 focus:border-pink-400",
            "placeholder": "000.000.000-00",
            "oninput": "formatCPF(this)",
            "onblur": "validateCPF()",
        })
    )
    group = forms.ChoiceField(
        label="Função",
        required=True,
        choices=[],
        widget=forms.Select(attrs={
            "class": "mt-1 block w-full rounded border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-pink-400 focus:border-pink-400"
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            "class": "mt-1 block w-full rounded border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-pink-400 focus:border-pink-400",
            "oninput": "updatePasswordStrength()"
        })
    )
    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            "class": "mt-1 block w-full rounded border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-pink-400 focus:border-pink-400",
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        grupos_validos = Group.objects.exclude(name__in=['admin', 'avaliadora'])
        choices = [('', 'Selecione um grupo')] + [(g.name, g.name.capitalize()) for g in grupos_validos]
        self.fields['group'].choices = choices

    def clean_email(self):
        email = self.cleaned_data['email']
        if not validar_email(email):
            raise forms.ValidationError("Email inválido.")
        return email

    def clean_cpf(self):
        cpf = self.cleaned_data['cpf']
        cpf_digits = re.sub(r'\D', '', cpf)
        if not validar_cpf(cpf_digits):
            raise forms.ValidationError("CPF inválido.")
        return cpf_digits  # retorna CPF limpo para salvar

    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get("password")
        confirmar = cleaned_data.get("confirm_password")

        if senha and confirmar and senha != confirmar:
            raise forms.ValidationError("Senhas não conferem.")

        if senha:
            senha_valida = validar_senha(senha)
            if senha_valida is not True:
                raise forms.ValidationError(senha_valida)

        return cleaned_data



from applications.drive.drive_services import DriveService


import logging
import traceback

logger = logging.getLogger(__name__)


class UserUpdateForm(forms.ModelForm):
    # BINARY_FILE_FIELDS = [
    #     'documento_cpf',
    #     'documento_rg',
    #     'foto',
    #     'autodeclaracao_racial',
    #     'comprovante_deficiencia',
    # ]
    
    DRIVE_UPLOAD_FIELDS = {
        'drive_rg_frente': "RG (frente)",
        'drive_rg_verso': "RG (verso)", 
        'drive_cpf_anexo': "CPF",
        'drive_foto': "Foto do Usuário",
        'drive_autodeclaracao_racial':"Autodeclaração para cotas",
        'drive_comprovante_deficiencia': "Comprovante de deficiência"
    }

    # for field_name in BINARY_FILE_FIELDS:

    #     display_label = get_binary_field_display_name(field_name)

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
        locals()[f"{field_name}__upload"].friendly_label = label 
        locals()[f"{field_name}__clear"] = forms.BooleanField(
            required=False,
            widget=forms.HiddenInput(),
            label=f"Remover arquivo atual do Drive"
        )
    del field_name, label

    nome = forms.CharField(
        label="Nome Completo",
        help_text="Por favor, digite seu nome completo, sem abreviações.", 
        required=True, 
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full',
            'placeholder': "Por favor, digite seu nome completo, sem abreviações."})
    )
    
    raca = forms.ModelChoiceField(
        queryset=Raca.objects.all(),
        label="Raça",
        empty_label="--------",
        required=True,
        widget=forms.Select(attrs={'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-pink-400 focus:border-pink-400'})
    )

    genero = forms.ModelChoiceField(
        queryset=Genero.objects.all(),
        label="Gênero",
        empty_label="--------",
        required=True,
        widget=forms.Select(attrs={'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-pink-400 focus:border-pink-400'})
    )
    
    deficiencias = forms.ModelMultipleChoiceField(
        queryset=Deficiencia.objects.all(),
        label="Deficiências",
        required=True,
        widget=forms.SelectMultiple(attrs={'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-pink-400 focus:border-pink-400'})
    )

    data_nascimento = forms.DateField(
        required=True,
        label="Data de nascimento",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'mt-1 block w-full', 'placeholder': "DD/MM/AAAA"})
    )

    telefone = forms.CharField(
        label="Telefone",
        help_text="Por favor, digite seu nome completo, sem abreviações.", 
        required=True, 
        widget=forms.TextInput(attrs={
            'class': 'mt-1 block w-full',
            'placeholder': "(XX) 9XXXX-XXXX"})
    )

    class Meta:
        model = User
        fields = [
            'cpf', 
            'email', 
            'nome', 
            'telefone', 
            'telefone_responsavel',
            'data_nascimento', 
            'pronomes',
            'curriculo_lattes',
            'raca', 'genero', 'deficiencias',
            'termo_responsabilidade', 'autodeclaracao'
        ]

        widgets = {
            'cpf': forms.TextInput(attrs={'readonly': 'readonly','placeholder': "000.000.000-00", 'class': 'mt-1 block w-full', 'oninput': "formatCPF(this)", 'onblur': "validateCPF()"}),
            'email': forms.EmailInput(attrs={'class': 'mt-1 block w-full', 'placeholder': "email@exemplo.com"}),
            'telefone_responsavel': forms.TextInput(attrs={'class': 'mt-1 block w-full', 'placeholder': "(XX) 9XXXX-XXXX"}),
            'pronomes': forms.TextInput(attrs={'class': 'mt-1 block w-full'}),
            'curriculo_lattes': forms.URLInput(attrs={'class': 'mt-1 block w-full', 'placeholder': "https://lattes.cnpq.br/XXXXXXXXXXXXXX"}),
        }
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Extrai o user dos kwargs
        super().__init__(*args, **kwargs)
        self.fields['cpf'].disabled = True
        self.fields['deficiencias'].required = False

        # Verifica se a instância já tem um arquivo salvo no Drive
        if self.instance and self.instance.pk:
            for field_name, label in self.DRIVE_UPLOAD_FIELDS.items():
                # Obtém o ID do arquivo do modelo
                file_id = getattr(self.instance, field_name, None)
                
                # Se o ID existe, adiciona o link ao campo de upload
                if file_id:
                    drive_link = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
                    
                    upload_field_name = f"{field_name}__upload"
                    
                    # Adiciona o atributo drive_link ao objeto do campo
                    self.fields[upload_field_name].drive_link = drive_link
                    
                    # Adiciona uma mensagem de ajuda mais clara
                    self.fields[upload_field_name].help_text = (
                        f"Um arquivo já foi enviado. Envie um novo para substituí-lo ou marque a caixa abaixo para remover."
                    )
        
        
    def clean_data_nascimento(self):
        data_nascimento = self.cleaned_data.get("data_nascimento")
        if not data_nascimento:
            return data_nascimento
        
        hoje = date.today()
        idade_minima = 12
        data_minima = date(hoje.year - idade_minima, hoje.month, hoje.day)
        
        if data_nascimento > data_minima:
            raise forms.ValidationError(f"Você deve ter no mínimo {idade_minima} anos para se cadastrar.")
        
        return data_nascimento

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
                
    def _upload_documents_to_drive(self, instance, drive_service=None):
        try:
            if not drive_service:
                drive_service = DriveService()
            
            # Verifica acesso antes de criar pasta
            if not drive_service.test_folder_access(settings.DRIVE_ROOT_FOLDER_ID):
                logger.error("Falha ao acessar a pasta raiz. Verifique se o ID e as credenciais estão corretos.")
                raise forms.ValidationError("Falha no acesso ao Google Drive. Contate o administrador.")
            
            logger.info("Iniciando upload para o Drive")
            
            # Cria o caminho perfil/CPF (se não existir)
            perfil_folder_name = "perfil"
            user_folder_name = instance.cpf
            logger.info(f"Verificando/Criando estrutura de pastas: {perfil_folder_name}/{user_folder_name}")
            
            # Primeiro verifica/cria a pasta 'perfil'
            perfil_folder_id = drive_service.find_or_create_folder(
                folder_name=perfil_folder_name,
                parent_folder_id=settings.DRIVE_ROOT_FOLDER_ID
            )
            logger.info(f"Pasta 'perfil' ID: {perfil_folder_id}")
            
            # Depois cria a pasta do usuário (CPF) dentro da pasta 'perfil'
            user_folder_id = drive_service.find_or_create_folder(
                folder_name=user_folder_name,
                parent_folder_id=perfil_folder_id
            )
            logger.info(f"Pasta do usuário criada com ID: {user_folder_id}")

            # Faz upload dos arquivos para a pasta do usuário
            for field_name in self.DRIVE_UPLOAD_FIELDS.keys():
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

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # # Associa o usuário logado ao instance
        # if self.user:
        #     instance.user = self.user  # Isso só é necessário se seu model User tiver um campo user (o que seria estranho)
        #     # Ou talvez você queira fazer:
        #     # instance = self.user  # Se você está atualizando o próprio usuário
        
        drive_service = DriveService()
        
        try:
            self._clear_documents_from_drive(instance, drive_service)
            self._upload_documents_to_drive(instance, drive_service)
        except forms.ValidationError:
            raise
        except Exception as e:
            logger.error(f"Erro geral no save: {str(e)}")
            if commit:
                instance.save()
            raise forms.ValidationError(
                "Ocorreu um erro ao processar seus documentos. "
                "Seu formulário foi salvo, mas você pode precisar reenviar os arquivos."
            )

        if commit:
            instance.save()
        return instance
    
    

    # def save(self, commit=True):
    #     instance = super().save(commit=False)
    #     self._apply_binary_uploads(instance)
    #     if commit:
    #         instance.save()
    #         self.save_m2m()
    #     return instance
     
