# apps/applications/forms.py
from __future__ import annotations
from typing import Any, Dict, Optional

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Application, ApplicationStatusLog


class ApplicationForm(forms.ModelForm):
    """
    Responsável por:
    - Validar dependências de campos (ex.: se necessita material, exigir descrição).
    - Converter uploads (UploadedFile) em bytes para BinaryField.
    - Manter campos não editáveis (usuario) fora do form.
    """

    # Map de campos binários para inputs de arquivo (facilita manutenção)
    BINARY_FILE_FIELDS = {
        "laudo_medico_deficiencia": _("Laudo Médico (PDF/Imagem)"),
        "autodeclaracao_racial": _("Autodeclaração Racial (PDF/Imagem)"),
        "boletim_escolar": _("Boletim Escolar (PDF/Imagem)"),
        "termo_autorizacao": _("Termo de Autorização (PDF/Imagem)"),
        "rg_frente": _("RG - Frente (Imagem)"),
        "rg_verso": _("RG - Verso (Imagem)"),
        "cpf_anexo": _("CPF (Imagem/PDF)"),
        "declaracao_vinculo": _("Declaração de Vínculo (PDF)"),
        "documentacao_comprobatoria_lattes": _("Comprobatórios Lattes (PDF)"),
    }

    # Propriedade para uso no template (nome sem underscore)
    @property
    def binary_file_fields(self):
        return self.BINARY_FILE_FIELDS

    # Criação dinâmica dos FileFields e checkboxes
    for _name, _label in BINARY_FILE_FIELDS.items():
        locals()[f"{_name}__upload"] = forms.FileField(
            label=_label, required=False,
            help_text=_("Envie um arquivo; deixe em branco para manter o atual.")
        )
        locals()[f"{_name}__clear"] = forms.BooleanField(
            label=_("Remover arquivo atual"), required=False
        )
    del _name, _label

    class Meta:
        model = Application
        # Campos exibidos (excluímos usuario; criado_em/atualizado_em são somente leitura)
        fields = [
            "projeto",
            "status",

            "como_soube_programa",
            "telefone_responsavel",
            "observacoes",
            "curriculo_lattes_url",

            "cota_desejada",
            "tipo_deficiencia",
            "necessita_material_especial",
            "tipo_material_necessario",
            "concorrer_reserva_vagas",
            "mulher_trans",

            # Trajetória
            "perfil_academico",
            "docencia_superior",
            "docencia_medio",
            "orientacao_ic",
            "feira_ciencias",
            "livro_publicado",
            "capitulo_publicado",
            "periodico_indexado",
            "anais_congresso",
            "curso_extensao",
            "curso_capacitacao",
            "orientacoes_estudantes",
            "participacoes_bancas",
            "apresentacao_oral",
            "premiacoes",
            "missao_cientifica",

            # Declarações
            "aceite_declaracao_veracidade",
            "aceite_requisitos_tecnicos",

            # Notas
            "portugues", "matematica", "biologia", "quimica",
            "fisica", "historia", "geografia",
        ]

        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
            "como_soube_programa": forms.Textarea(attrs={"rows": 3}),
            "observacoes": forms.Textarea(attrs={"rows": 3}),
            "tipo_material_necessario": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        # UX: campo tipo_material_necessario só faz sentido quando necessita_material_especial=True
        self.fields["tipo_material_necessario"].required = False

    # ---------- Validações de domínio ----------
    def clean(self) -> Dict[str, Any]:
        cleaned = super().clean()

        if cleaned.get("necessita_material_especial") and not cleaned.get("tipo_material_necessario"):
            raise ValidationError({"tipo_material_necessario": _("Descreva o material especial necessário.")})

        # Se concorrer à reserva de vagas e houver autodeclaração, tudo ok; não tornamos obrigatório pois o modelo permite blank
        # (caso queira forçar upload quando concorrer_reserva_vagas=True, descomente abaixo)
        # if cleaned.get("concorrer_reserva_vagas") and not self.files.get("autodeclaracao_racial__upload"):
        #     raise ValidationError({"autodeclaracao_racial__upload": _("Envie a autodeclaração racial.")})

        # Aceites
        if not cleaned.get("aceite_declaracao_veracidade"):
            raise ValidationError({"aceite_declaracao_veracidade": _("É necessário aceitar a declaração de veracidade.")})
        if not cleaned.get("aceite_requisitos_tecnicos"):
            raise ValidationError({"aceite_requisitos_tecnicos": _("É necessário aceitar os requisitos técnicos.")})

        return cleaned

    # ---------- Persistência dos BinaryFields ----------
    def _apply_binary_uploads(self, instance: Application) -> None:
        for field_name in self.BINARY_FILE_FIELDS.keys():
            upload_field = f"{field_name}__upload"
            clear_field = f"{field_name}__clear"
            if self.cleaned_data.get(clear_field):
                setattr(instance, field_name, None)
                continue
            uploaded = self.files.get(upload_field)
            if uploaded:
                setattr(instance, field_name, uploaded.read())

                
    def save(self, commit: bool = True) -> Application:
        # Guardar status antigo para log
        old_status: Optional[str] = None
        if self.instance and self.instance.pk:
            old_status = Application.objects.filter(pk=self.instance.pk).values_list("status", flat=True).first()

        instance: Application = super().save(commit=False)

        # Aplica uploads binários
        self._apply_binary_uploads(instance)

        if commit:
            instance.save()
            self.save_m2m()

            # Log de mudança de status (somente se alterou)
            new_status = instance.status
            if old_status != new_status:
                ApplicationStatusLog.objects.create(
                    inscricao=instance,
                    projeto=instance.projeto,
                    status_anterior=old_status,
                    status_novo=new_status,
                    status_anterior_display=dict(Application.STATUS_ESCOLHAS).get(old_status) if old_status else None,
                    status_novo_display=dict(Application.STATUS_ESCOLHAS).get(new_status),
                    modificado_por=f"{self.request.user.get_full_name() or self.request.user.username} <{self.request.user.email}>"
                    if self.request and self.request.user.is_authenticated else None
                )
        return instance
