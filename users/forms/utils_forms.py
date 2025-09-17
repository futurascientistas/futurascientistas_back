from django import forms
from users.models.school_model import Escola
from users.models.school_transcript_model import HistoricoEscolar, Disciplina, Nota
from django.forms import inlineformset_factory

# class NotaForm(forms.ModelForm):
#     disciplina_nome = forms.CharField(max_length=100, label="Disciplina", required=True)
    
#     class Meta:
#         model = Nota
#         fields = ['bimestre', 'valor']
#         widgets = {
#             'bimestre': forms.Select(attrs={'class': 'seu-estilo-css'}),
#             'valor': forms.NumberInput(attrs={'class': 'seu-estilo-css', 'step': '0.01'}),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
    
#     def save(self, commit=True):
#         disciplina_nome = self.cleaned_data.get('disciplina_nome')

#         disciplina_obj, created = Disciplina.objects.get_or_create(nome=disciplina_nome)

#         self.instance.disciplina = disciplina_obj
        
#         return super().save(commit=commit)

class NotaForm(forms.ModelForm):
    disciplina = forms.ModelChoiceField(
        queryset=Disciplina.objects.all(),
        label="Disciplina",
        widget=forms.Select(attrs={'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2'}),
        empty_label="Selecione uma disciplina"
    )

    class Meta:
        model = Nota
        fields = ['disciplina', 'bimestre', 'tipo_conceito', 'valor', 'nota_original']
        widgets = {
            'bimestre': forms.Select(attrs={'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2'}),
            'tipo_conceito': forms.Select(attrs={'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2'}),
            'valor': forms.NumberInput(attrs={'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2', 'step': '0.01'}),
            'nota_original': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2'}),
        }

HistoricoNotaFormSet = inlineformset_factory(
    parent_model=Nota._meta.get_field('historico').related_model,
    model=Nota,
    form=NotaForm,
    fields=['disciplina', 'bimestre', 'tipo_conceito', 'valor', 'nota_original'],
    extra=1,
    can_delete=True
)