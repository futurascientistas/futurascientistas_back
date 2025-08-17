from django import forms
from users.models.school_model import Escola, TipoEnsino

class EscolaForm(forms.ModelForm):
    class Meta:
        model = Escola
        fields = ['nome_escola', 'tipo_ensino', 'telefone_escola', 'telefone_responsavel_escola']

    nome_escola = forms.CharField(
        required=True, 
        label="Nome da escola",
        help_text="Por favor, digite seu nome completo, sem abreviações.", 
        widget=forms.TextInput(attrs={'placeholder': 'Ex: Por favor, digite o nome completo da escola sem abreviações.', 'class': 'mt-1 block w-full'})
    )
    telefone_escola = forms.CharField(
        required=True, 
        label="Telefone da escola",
        widget=forms.TextInput(attrs={'placeholder': '(XX) 9XXXX-XXXX'})
    )
    telefone_responsavel_escola = forms.CharField(
        required=True, 
        label="Telefone do responsável da escola",
        widget=forms.TextInput(attrs={'placeholder': '(XX) 9XXXX-XXXX'})
    )
    tipo_ensino = forms.ModelChoiceField(
        queryset=TipoEnsino.objects.all(),
        label="Tipo de Ensino",
        empty_label="--------",
        required=True,
        widget=forms.Select(attrs={'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-pink-400 focus:border-pink-400'})
    )