from django import forms

from utils.utils import get_binary_field_display_name
from .models import *
from projects.models import *
from users.models import *
from ckeditor.fields import RichTextField
from django.utils import timezone
from django.db.models import Q


class ApplicationAlunoForm(forms.ModelForm):
    BINARY_FILE_FIELDS = [
        'rg_frente',
        'rg_verso',
        'cpf_anexo',
        'declaracao_inclusao'
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
    
    tamanho_jaleco = forms.ChoiceField(
        choices=[('', 'Selecione um tamanho')] + list(Application.JALECO_CHOICES),
        label="Selecione um tamanho para o jaleco",
        required=True,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2',
        })
    )

    for field_name in BINARY_FILE_FIELDS:

        display_label = display_label = get_binary_field_display_name(field_name)

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

    class Meta:
        model = Application
        fields = [
            'projeto',
            'tipo_de_vaga',
            'tamanho_jaleco',
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
        'declaracao_inclusao',
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

    tipo_de_vaga = forms.ModelChoiceField(
        queryset=TipoDeVaga.objects.all(),  
        label="Tipo de Vaga",
        empty_label="Selecione um tipo de vaga",
        required=True,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2',
        })
    )

    grau_formacao = forms.ChoiceField(
        choices=[('', 'Selecione um Grau de Formação')] + list(GrauFormacao.choices),
        label="Grau de formação mais alto",
        required=False,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2',
        })
    )

    # modalidade_vaga = forms.ChoiceField(
    #     choices=[('', 'Selecione uma modalidade')] + list(GrauFormacao.choices),
    #     label="Selecione uma modalidade de vaga",
    #     required=True,
    #     widget=forms.Select(attrs={
    #         'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2',
    #     })
    # )
    
    tamanho_jaleco = forms.ChoiceField(
        choices=[('', 'Selecione um tamanho')] + list(Application.JALECO_CHOICES),
        label="Selecione um tamanho para o jaleco",
        required=True,
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2',
        })
    )

    tipo_deficiencia = forms.ModelChoiceField(
        queryset=Deficiencia.objects.all(),  
        label="Deficiencia",
        required=True,
        empty_label="Selecione uma deficiencia",
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full rounded border border-gray-300 px-3 py-2',
        })
    )

    CUSTOM_FIELD_LABELS = {
        'rg_frente': 'RG (frente)', 
        'rg_verso': 'RG (verso)',   
        'cpf_anexo': 'CPF',
    }

    for field_name in BINARY_FILE_FIELDS:

        display_label = CUSTOM_FIELD_LABELS.get(field_name, field_name.replace('_', ' ').capitalize())

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

    class Meta:
        model = Application
        fields = [
            # --- Dados gerais ---
            'projeto',
            'como_soube_programa',
            'curriculo_lattes_url',
            'tamanho_jaleco',
            'area_atuacao',
            'tipo_de_vaga',
            'tipo_deficiencia',
            'necessita_material_especial',
            'tipo_material_necessario',
            'curriculo_lattes_url',

            # --- Formação e perfil ---
            'grau_formacao',
            'perfil_academico',

            # --- Experiência docente ---
            'docencia_superior',
            'docencia_medio',
            'orientacoes_estudantes',
            'participacoes_bancas',

            # --- Produção científica ---
            'periodico_indexado',
            'livro_publicado',
            'capitulo_publicado',
            'anais_congresso',
            'apresentacao_oral',

            # --- Projetos, cursos e eventos ---
            'orientacao_ic',
            'feira_ciencias',
            'curso_extensao',
            'curso_capacitacao',
            'premiacoes',
            'missao_cientifica',

            # --- Projeto submetido ---
            'titulo_projeto_submetido',
            'link_projeto',
            'numero_edicoes_participadas',

            # --- Termos de aceite ---
            'aceite_declaracao_veracidade',
            'aceite_requisitos_tecnicos',
        ]


        widgets = {
            'como_soube_programa': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Como soube do programa?'}),
            'curriculo_lattes_url': forms.URLInput(attrs={'placeholder': 'URL do Currículo Lattes'}),
            'area_atuacao': forms.TextInput(attrs={'placeholder': 'Área de atuação'}),
            'tipo_de_vaga': forms.TextInput(attrs={'placeholder': 'Tipo de Vaga'}),
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
            #inicio_inscricoes__lte=hoje,
            #fim_inscricoes__gte=hoje,
        )

        if user:
            estado_usuario = getattr(user, 'cidade', None)
            # Verifica se estado_usuario é um objeto válido (não vazio, não string vazia)
            if estado_usuario and hasattr(estado_usuario, 'id'):
                projetos = projetos.filter(
                    Q(cidades_aceitas__isnull=True) | Q(cidades_aceitas=estado_usuario)
                ).distinct()
            else:
                # Se não tem estado válido, só mostra os que não tem estado restrito
                projetos = projetos.filter(cidades_aceitas__isnull=True)

        else:
            projetos = Project.objects.none()

        self.fields['projeto'].queryset = projetos


class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['comentario']