from django import template

register = template.Library()

@register.filter
def is_in(value, arg):
    """Comprobar si un valor está en una lista o conjunto"""
    return value in arg