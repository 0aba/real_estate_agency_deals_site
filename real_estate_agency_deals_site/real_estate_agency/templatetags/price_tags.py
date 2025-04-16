from django import template


register = template.Library()

@register.filter
def subtract(value, arg):
    return value - arg

@register.filter
def next_value(l, i):
    try:
        return l[i+1]
    except ...:
        return None
