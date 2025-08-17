import re
from django import forms
from django.contrib.auth.models import Group
from utils.utils import get_binary_field_display_name
from users.services import validar_email, validar_cpf, validar_senha
from users.models import TipoEnsino
from users.models import Deficiencia, Genero, Raca, User

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


class UserUpdateForm(forms.ModelForm):
    BINARY_FILE_FIELDS = [
        'documento_cpf',
        'documento_rg',
        'foto',
        'autodeclaracao_racial',
        'comprovante_deficiencia',
    ]

    for field_name in BINARY_FILE_FIELDS:

        display_label = get_binary_field_display_name(field_name)

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
        super().__init__(*args, **kwargs)
        self.fields['cpf'].disabled = True

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
     
