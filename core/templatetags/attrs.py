# apps/core/templatetags/attrs.py  (crie o pacote templatetags)
from django import template
register = template.Library()

@register.filter
def attr(obj, name):
    return getattr(obj, name, None)
