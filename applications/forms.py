from django import forms
from .models import Application, GrauFormacao
from projects.models import *

class ApplicationAlunoForm(forms.ModelForm):
    BINARY_FILE_FIELDS = [
        'rg_frente',
        'rg_verso',
        'cpf_anexo',
        'declaracao_vinculo',
        'documentacao_comprobatoria_lattes',
    ]

    projeto = forms.ModelChoiceField(
        queryset=Project.objects.all(),  
        label="Projeto",
        empty_label="Selecione um projeto",
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2',
        })
    )

    for field_name in BINARY_FILE_FIELDS:
        locals()[f"{field_name}__upload"] = forms.FileField(
            required=False,
            label=f"Enviar arquivo para {field_name.replace('_', ' ').capitalize()}",
            help_text="Deixe em branco para manter o arquivo atual."
        )
        locals()[f"{field_name}__clear"] = forms.BooleanField(
            required=False,
            label=f"Remover arquivo atual de {field_name.replace('_', ' ').capitalize()}"
        )
    del field_name

    class Meta:
        model = Application
        fields = [
            'projeto',
            'como_soube_programa',
            'telefone_responsavel',
            'curriculo_lattes_url',
            'area_atuacao',
            'cota_desejada',
            'tipo_deficiencia',
            'necessita_material_especial',
            'tipo_material_necessario',
            'concorrer_reserva_vagas',
            'mulher_trans',
            'grau_formacao',
            'perfil_academico',
            'docencia_superior',
            'docencia_medio',
            'orientacao_ic',
            'feira_ciencias',
            'livro_publicado',
            'capitulo_publicado',
            'periodico_indexado',
            'anais_congresso',
            'curso_extensao',
            'curso_capacitacao',
            'orientacoes_estudantes',
            'participacoes_bancas',
            'apresentacao_oral',
            'premiacoes',
            'missao_cientifica',
            'titulo_projeto_submetido',
            'link_projeto',
            'numero_edicoes_participadas',
            'aceite_declaracao_veracidade',
            'aceite_requisitos_tecnicos',
        ]

        widgets = {
            'como_soube_programa': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Como soube do programa?'}),
            'telefone_responsavel': forms.TextInput(attrs={'placeholder': 'Telefone da responsável'}),
            'curriculo_lattes_url': forms.URLInput(attrs={'placeholder': 'URL do Currículo Lattes'}),
            'area_atuacao': forms.TextInput(attrs={'placeholder': 'Área de atuação'}),
            'cota_desejada': forms.TextInput(attrs={'placeholder': 'Cota desejada'}),
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


    def clean_numero_edicoes_participadas(self):
        num = self.cleaned_data.get('numero_edicoes_participadas')
        if num is not None and num < 0:
            raise forms.ValidationError("Número de edições anteriores não pode ser negativo.")
        return num


class ApplicationProfessorForm(forms.ModelForm):

    BINARY_FILE_FIELDS = [
        'rg_frente',
        'rg_verso',
        'cpf_anexo',
        'declaracao_vinculo',
        'documentacao_comprobatoria_lattes',
    ]

    projeto = forms.ModelChoiceField(
        queryset=Project.objects.all(),  
        label="Projeto",
        empty_label="Selecione um projeto",
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2',
        })
    )

    for field_name in BINARY_FILE_FIELDS:
        locals()[f"{field_name}__upload"] = forms.FileField(
            required=False,
            label=f"Enviar arquivo para {field_name.replace('_', ' ').capitalize()}",
            help_text="Deixe em branco para manter o arquivo atual."
        )
        locals()[f"{field_name}__clear"] = forms.BooleanField(
            required=False,
            label=f"Remover arquivo atual de {field_name.replace('_', ' ').capitalize()}"
        )
    del field_name

    class Meta:
        model = Application
        fields = [
            'projeto',
            'como_soube_programa',
            'telefone_responsavel',
            'curriculo_lattes_url',
            'area_atuacao',
            'cota_desejada',
            'tipo_deficiencia',
            'necessita_material_especial',
            'tipo_material_necessario',
            'concorrer_reserva_vagas',
            'mulher_trans',
            'grau_formacao',
            'perfil_academico',
            'docencia_superior',
            'docencia_medio',
            'orientacao_ic',
            'feira_ciencias',
            'livro_publicado',
            'capitulo_publicado',
            'periodico_indexado',
            'anais_congresso',
            'curso_extensao',
            'curso_capacitacao',
            'orientacoes_estudantes',
            'participacoes_bancas',
            'apresentacao_oral',
            'premiacoes',
            'missao_cientifica',
            'titulo_projeto_submetido',
            'link_projeto',
            'numero_edicoes_participadas',
            'aceite_declaracao_veracidade',
            'aceite_requisitos_tecnicos',
        ]

        widgets = {
            'como_soube_programa': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Como soube do programa?'}),
            'telefone_responsavel': forms.TextInput(attrs={'placeholder': 'Telefone da responsável'}),
            'curriculo_lattes_url': forms.URLInput(attrs={'placeholder': 'URL do Currículo Lattes'}),
            'area_atuacao': forms.TextInput(attrs={'placeholder': 'Área de atuação'}),
            'cota_desejada': forms.TextInput(attrs={'placeholder': 'Cota desejada'}),
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


    def clean_numero_edicoes_participadas(self):
        num = self.cleaned_data.get('numero_edicoes_participadas')
        if num is not None and num < 0:
            raise forms.ValidationError("Número de edições anteriores não pode ser negativo.")
        return num
