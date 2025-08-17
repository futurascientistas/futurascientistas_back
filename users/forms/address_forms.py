from django import forms
from users.models.address_model import Endereco, Estado

class EnderecoForm(forms.ModelForm):
    class Meta:
        model = Endereco
        fields = '__all__' 

    estado = forms.ModelChoiceField(
        queryset=Estado.objects.all(),
        label="Estado",
        required=True
    )
    cep = forms.CharField(
        required=True, 
        label="CEP",
        widget=forms.TextInput(attrs={'placeholder': 'Ex: 99999-999'})
    )
    cidade = forms.CharField(
        required=True, 
        label="Cidade",
        widget=forms.TextInput(attrs={'placeholder': 'Ex: Cidade Exemplo'})
    )
    bairro = forms.CharField(
        required=True, 
        label="Bairro",
        widget=forms.TextInput(attrs={'placeholder': 'Ex: Bairro Exemplo'})
    )
    rua = forms.CharField(
        required=True, 
        label="Rua",
        widget=forms.TextInput(attrs={'placeholder': 'Ex: Rua Principal'})
    )
    numero = forms.CharField(
        required=True, 
        label="Número",
        widget=forms.TextInput(attrs={'placeholder': 'Ex: 123'})
    )