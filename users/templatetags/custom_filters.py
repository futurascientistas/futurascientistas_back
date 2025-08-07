from django import template

register = template.Library()

@register.filter
def get_value_for_key(list_of_dicts, key):
    """
    Retorna uma lista de valores para uma chave específica
    de uma lista de dicionários.
    """
    return [d.get(key) for d in list_of_dicts if isinstance(d, dict)]