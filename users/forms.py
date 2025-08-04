from django import forms
import re
from django.contrib.auth.models import Group
from .services import validar_email, validar_cpf, validar_senha

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
        label="Grupo",
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
