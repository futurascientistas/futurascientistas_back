from django import forms
from .models import *
from projects.models import *
from users.models import *
from ckeditor.fields import RichTextField
from django.utils import timezone
from django.db.models import Q


class ApplicationAlunoForm(forms.ModelForm):
    # Apenas os campos BinaryField para upload de documentos de identificação
    # foram mantidos. Os outros foram removidos para simplificar.
    BINARY_FILE_FIELDS = [
        'rg_frente',
        'rg_verso',
        'cpf_anexo',
    ]

    projeto = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        label="Projeto",
        empty_label="Selecione um projeto",
        required=True,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2',
        })
    )

    necessita_material_especial = forms.BooleanField(
        label="Necessita de material especial?",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'})
    )

    tipo_material_necessario = forms.CharField(
        label="Indicar o tipo de material necessário",
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Ex: Material impresso em braile, Material impresso ampliado'}),
        required=False
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
            'cota_desejada',
            'tipo_deficiencia',
            'necessita_material_especial',
            'tipo_material_necessario',
            'aceite_declaracao_veracidade',
            'aceite_requisitos_tecnicos',
        ]

        widgets = {
            'aceite_declaracao_veracidade': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'aceite_requisitos_tecnicos': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
        
    def _apply_binary_uploads(self, instance):
        for field_name in self.BINARY_FILE_FIELDS:
            upload_field_name = f"{field_name}__upload"
            clear_field_name = f"{field_name}__clear"
            
            if self.cleaned_data.get(clear_field_name):
                setattr(instance, field_name, None)
            
            uploaded_file = self.files.get(upload_field_name)
            if uploaded_file:
                setattr(instance, field_name, uploaded_file.read())

    def save(self, commit=True):
        instance = super().save(commit=False)
        self._apply_binary_uploads(instance)
        if commit:
            instance.save()
        return instance

    def clean(self):
        cleaned_data = super().clean()
        
        if not cleaned_data.get('projeto'):
            self.add_error('projeto', 'O projeto é obrigatório.')
        if not cleaned_data.get('aceite_declaracao_veracidade'):
            self.add_error('aceite_declaracao_veracidade', 'É necessário aceitar a declaração de veracidade.')
        if not cleaned_data.get('aceite_requisitos_tecnicos'):
            self.add_error('aceite_requisitos_tecnicos', 'É necessário aceitar os requisitos técnicos.')
            
        necessita_material = cleaned_data.get('necessita_material_especial')
        tipo_material = cleaned_data.get('tipo_material_necessario')
        
        if necessita_material and not tipo_material:
            self.add_error('tipo_material_necessario', 'Por favor, indique o tipo de material necessário.')

        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        hoje = timezone.now().date()
        projetos = Project.objects.filter(
            ativo=True,
            inicio_inscricoes__lte=hoje,
            fim_inscricoes__gte=hoje,
        )

        if user:
            estado_usuario = getattr(user, 'estado', None)
            # Verifica se estado_usuario é um objeto válido (não vazio, não string vazia)
            if estado_usuario and hasattr(estado_usuario, 'id'):
                projetos = projetos.filter(
                    Q(estados_aceitos__isnull=True) | Q(estados_aceitos=estado_usuario)
                ).distinct()
            else:
                # Se não tem estado válido, só mostra os que não tem estado restrito
                projetos = projetos.filter(estados_aceitos__isnull=True)

        else:
            projetos = Project.objects.none()

        self.fields['projeto'].queryset = projetos



class ApplicationProfessorForm(forms.ModelForm):

    BINARY_FILE_FIELDS = [
        'rg_frente',
        'rg_verso',
        'cpf_anexo',
        'declaracao_vinculo',
        'documentacao_comprobatoria_lattes',
    ]

    projeto = forms.ModelChoiceField(
        queryset=Project.objects.none(),  
        label="Projeto",
        empty_label="Selecione um projeto",
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2',
        })
    )

    cota_desejada = forms.ModelChoiceField(
        queryset=Cota.objects.all(),  
        label="Cota",
        empty_label="Selecione uma cota",
         required=False,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2',
        })
    )

    tipo_deficiencia = forms.ModelChoiceField(
        queryset=Deficiencia.objects.all(),  
        label="Deficiencia",
         required=False,
        empty_label="Selecione uma deficiencia",
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
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        hoje = timezone.now().date()
        projetos = Project.objects.filter(
            ativo=True,
            inicio_inscricoes__lte=hoje,
            fim_inscricoes__gte=hoje,
        )

        if user:
            estado_usuario = getattr(user, 'estado', None)
            # Verifica se estado_usuario é um objeto válido (não vazio, não string vazia)
            if estado_usuario and hasattr(estado_usuario, 'id'):
                projetos = projetos.filter(
                    Q(estados_aceitos__isnull=True) | Q(estados_aceitos=estado_usuario)
                ).distinct()
            else:
                # Se não tem estado válido, só mostra os que não tem estado restrito
                projetos = projetos.filter(estados_aceitos__isnull=True)

        else:
            projetos = Project.objects.none()

        self.fields['projeto'].queryset = projetos


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['comentario']