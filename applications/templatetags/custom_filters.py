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

@register.filter
def attr(obj, attr_name):
    return getattr(obj, attr_name, '')

@register.filter
def get_display(obj, field_name):
    # 1 - tenta pegar o método get_FOO_display() (para choices)
    method_name = f'get_{field_name}_display'
    method = getattr(obj, method_name, None)

    if callable(method):
        return method()

    # 2 - pega o valor do campo
    value = getattr(obj, field_name, None)

    # 3 - Trata boolean como Verdadeiro/Falso
    if isinstance(value, bool):
        return "Verdadeiro" if value else "Falso"
    if isinstance(value, (str, int)):
        if str(value).lower() in ["true", "1"]:
            return "Verdadeiro"
        if str(value).lower() in ["false", "0"]:
            return "Falso"

    # 4 - Se for objeto relacionado, usa __str__()
    if hasattr(value, '__str__'):
        return str(value)

    return value if value is not None else ''

