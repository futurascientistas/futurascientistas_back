from django import template
from django.core.exceptions import FieldDoesNotExist

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Permite acessar um item de um dicionário (ou atributo de um objeto)
    usando uma chave dinâmica no template.
    Ex: {{ my_dict|get_item:key_name }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)

    return getattr(dictionary, key, None)

@register.filter(name='get_model_field_verbose_name')
def get_model_field_verbose_name(instance, field_name):
    """
    Retorna o verbose_name de um campo de um modelo Django.
    Útil para exibir o nome amigável de campos BinaryField em loops.
    Ex: {{ form.instance|get_model_field_verbose_name:'rg_frente' }}
    """
    try:

        field = instance._meta.get_field(field_name)
        return field.verbose_name
    except FieldDoesNotExist:

        return field_name.replace('_', ' ').capitalize()

