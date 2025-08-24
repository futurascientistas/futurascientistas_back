from django import forms
from core.models import Cidade, CidadesMaterializedView, Estado
from users.models.address_model import Endereco

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
    
    # cidade = forms.ModelChoiceField(
    #     queryset=Cidade.objects.all(),
    #     label="Cidade",
    #     required=True
    # )

    cidade = forms.ModelChoiceField(
        queryset=CidadesMaterializedView.objects.all().order_by('nome'),
        label="Cidade",
        required=True
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

    def clean_cidade(self):
        cidade_materialized = self.cleaned_data.get('cidade')
        if cidade_materialized:
            try:
                return Cidade.objects.get(pk=cidade_materialized.pk)
            except Cidade.DoesNotExist:
                raise forms.ValidationError("A cidade selecionada não é válida.")
        return cidade_materialized

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    #     estado_valor = None
    #     if 'estado' in self.data:
    #         try:
    #             estado_valor = int(self.data.get('estado'))
    #         except (ValueError, TypeError):
    #             pass
    #     elif self.instance.pk and self.instance.estado:
    #         estado_valor = self.instance.estado.id

    #     if estado_valor:
    #         self.fields['cidade'].queryset = Cidade.objects.filter(estado_id=estado_valor).order_by('nome')
    #     else:
    #         self.fields['cidade'].queryset = Cidade.objects.none()
        
    #     if 'cidade' in self.data:
    #         try:
    #             self.fields['cidade'].initial = int(self.data.get('cidade'))
    #         except (ValueError, TypeError):
    #             pass