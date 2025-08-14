
def get_binary_field_display_name(field_name):
    
    custom_labels = {
        'rg_frente': 'RG (frente)',
        'rg_verso': 'RG (verso)',
        'cpf_anexo': 'CPF',
        'documento_rg': 'RG ',
        'documento_cpf': 'CPF',
    }

    return custom_labels.get(field_name, field_name.replace('_', ' ').capitalize())
