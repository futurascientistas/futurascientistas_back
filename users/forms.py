import re
from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.models import Group
from .services import validar_email, validar_cpf, validar_senha
from .models import HistoricoEscolar, Nota, Disciplina, TipoEnsino


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


from .models import Deficiencia, Genero, Raca, User

class UserUpdateForm(forms.ModelForm):
    BINARY_FILE_FIELDS = [
        'documento_cpf',
        'documento_rg',
        'foto',
        'autodeclaracao_racial',
        'comprovante_deficiencia',
        'comprovante_autorizacao_responsavel'
    ]

    for field_name in BINARY_FILE_FIELDS:
        locals()[f"{field_name}__upload"] = forms.FileField(
            label=f"Enviar arquivo para {field_name.replace('_', ' ').capitalize()}",
            required=False,
            help_text="Deixe em branco para manter o arquivo atual."
        )
        locals()[f"{field_name}__clear"] = forms.BooleanField(
            label=f"Remover arquivo atual de {field_name.replace('_', ' ').capitalize()}",
            required=False
        )
    del field_name  

    raca = forms.ModelChoiceField(
        queryset=Raca.objects.all(),
        label="Raça",
        empty_label="--------",
        required=False,
        widget=forms.Select(attrs={'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-pink-400 focus:border-pink-400'})
    )

    genero = forms.ModelChoiceField(
        queryset=Genero.objects.all(),
        label="Gênero",
        empty_label="--------",
        required=False,
        widget=forms.Select(attrs={'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-pink-400 focus:border-pink-400'})
    )
    
    deficiencias = forms.ModelMultipleChoiceField(
        queryset=Deficiencia.objects.all(),
        label="Deficiências",
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-pink-400 focus:border-pink-400'})
    )
    tipo_ensino = forms.ModelChoiceField(
        queryset=TipoEnsino.objects.all(),  
        label="Tipo de Ensino",
        required=True,
        empty_label="--------",
        widget=forms.Select(attrs={'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-pink-400 focus:border-pink-400'})
    )

    class Meta:
        model = User
        fields = [
            'cpf', 'email', 'nome', 'telefone', 'telefone_responsavel','data_nascimento', 'pronomes',
            'curriculo_lattes',
            'cep', 'rua', 'bairro', 'numero', 'complemento', 'cidade', 'estado',
            'raca', 'genero', 'deficiencias',
            'nome_escola', 'tipo_ensino', 'cep_escola', 'rua_escola', 'bairro_escola',
            'numero_escola', 'complemento_escola', 'cidade_escola', 'estado_escola',
            'telefone_escola', 'telefone_responsavel_escola',
        ]

        labels = {
            'telefone_responsavel': 'Telefone Responsável',
            'telefone_responsavel_escola': 'Telefone Responsável da Escola',
        }

        widgets = {
            'cpf': forms.TextInput(attrs={'readonly': 'readonly'}),
            'email': forms.EmailInput(attrs={'class': 'mt-1 block w-full'}),
            'nome': forms.TextInput(attrs={'class': 'mt-1 block w-full'}),
            'telefone': forms.TextInput(attrs={'class': 'mt-1 block w-full'}),
            'telefone_responsavel': forms.TextInput(attrs={'class': 'mt-1 block w-full'}),
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'mt-1 block w-full'}),
            'pronomes': forms.TextInput(attrs={'class': 'mt-1 block w-full'}),
            'curriculo_lattes': forms.URLInput(attrs={'class': 'mt-1 block w-full'}),
            'cep': forms.TextInput(attrs={'class': 'mt-1 block w-full'}),
            'rua': forms.TextInput(attrs={'class': 'mt-1 block w-full'}),
            'bairro': forms.TextInput(attrs={'class': 'mt-1 block w-full'}),
            'numero': forms.TextInput(attrs={'class': 'mt-1 block w-full'}),
            'complemento': forms.TextInput(attrs={'class': 'mt-1 block w-full'}),
            'cidade': forms.TextInput(attrs={'class': 'mt-1 block w-full'}),
            'estado': forms.TextInput(attrs={'class': 'mt-1 block w-full'}),
            # 'raca': forms.Select(attrs={'class': 'mt-1 block w-full'}),
            # 'genero': forms.Select(attrs={'class': 'mt-1 block w-full'}),
            # 'deficiencias': forms.SelectMultiple(attrs={'class': 'mt-1 block w-full'}),
            'nome_escola': forms.TextInput(attrs={'class': 'mt-1 block w-full'}),
            'tipo_ensino': forms.TextInput(attrs={'class': 'mt-1 block w-full'}),
            'cep_escola': forms.TextInput(attrs={'class': 'mt-1 block w-full'}),
            'rua_escola': forms.TextInput(attrs={'class': 'mt-1 block w-full'}),
            'bairro_escola': forms.TextInput(attrs={'class': 'mt-1 block w-full'}),
            'numero_escola': forms.TextInput(attrs={'class': 'mt-1 block w-full'}),
            'complemento_escola': forms.TextInput(attrs={'class': 'mt-1 block w-full'}),
            'cidade_escola': forms.TextInput(attrs={'class': 'mt-1 block w-full'}),
            'estado_escola': forms.TextInput(attrs={'class': 'mt-1 block w-full'}),
            'telefone_escola': forms.TextInput(attrs={'class': 'mt-1 block w-full'}),
            'telefone_responsavel_escola': forms.TextInput(attrs={'class': 'mt-1 block w-full'}),
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
    
class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = ['disciplina', 'bimestre', 'valor']
        widgets = {
            'bimestre': forms.Select(attrs={'class': 'seu-estilo-css'}),
            'valor': forms.NumberInput(attrs={'class': 'seu-estilo-css', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['disciplina'].queryset = Disciplina.objects.all()

HistoricoNotaFormSet = inlineformset_factory(
    HistoricoEscolar,
    Nota,
    form=NotaForm,
    fields=['disciplina', 'bimestre', 'valor'],
    extra=1, 
    can_delete=True
)