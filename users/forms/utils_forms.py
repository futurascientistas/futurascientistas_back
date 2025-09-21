from django import forms
from users.forms.user_forms import UserUpdateForm
from users.models.school_model import Escola
from users.models.school_transcript_model import HistoricoEscolar, Disciplina, Nota
from django.forms import inlineformset_factory

from users.models.user_model import User

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
        fields = ['disciplina', 'bimestre', 'tipo_conceito', 'nota_original']
        widgets = {
            'bimestre': forms.Select(attrs={'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2'}),
            'tipo_conceito': forms.Select(attrs={'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2'}),
            'nota_original': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2'}),
        }

# class HistoricoEscolarForm(forms.ModelForm):
#     historico_escolar_upload = forms.FileField(
#         label="Histórico Escolar",
#         required=False,
#         widget=forms.ClearableFileInput(attrs={'class': 'mt-1 block w-full'}),
#         help_text="O arquivo será salvo no Google Drive."
#     )
    
#     class Meta:
#         model = HistoricoEscolar
#         fields = []

HistoricoNotaFormSet = inlineformset_factory(
    parent_model=Nota._meta.get_field('historico').related_model,
    model=Nota,
    form=NotaForm,
    fields=['disciplina', 'bimestre', 'valor', 'tipo_conceito', 'nota_original'],
    extra=0, 
    can_delete=False
)

class BoletimUploadForm(UserUpdateForm):
    class Meta:
        model = User
        fields = ['drive_boletim_escolar']

