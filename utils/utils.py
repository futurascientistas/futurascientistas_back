from django.core.validators import RegexValidator, FileExtensionValidator

def get_binary_field_display_name(field_name):
    
    custom_labels = {
        'rg_frente': 'RG (frente)',
        'rg_verso': 'RG (verso)',
        'cpf_anexo': 'CPF',
        'documento_rg': 'RG ',
        'documento_cpf': 'CPF',
        'comprovante_deficiencia' : 'comprovante de deficiência',
        'comprovante_autorizacao_responsavel': 'comprovante de autorização do responsável',
    }

    return custom_labels.get(field_name, field_name.replace('_', ' ').capitalize())

# Validadores
cpf_validator = RegexValidator(regex=r'^\d{11}$', message='CPF deve conter 11 dígitos numéricos.')
phone_validator = RegexValidator(regex=r'^\+?1?\d{9,15}$', message='Telefone inválido.')
extensoes_aceitas = FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])
cep_validator = RegexValidator(regex=r'^\d{5}-?\d{3}$', message='CEP deve estar no formato 12345-678 ou 12345678.') 
estado_validator = RegexValidator(regex=r'^[A-Z]{2}$', message='Estado deve ser a sigla de 2 letras maiúsculas.')
