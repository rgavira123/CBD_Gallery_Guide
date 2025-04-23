from django import template

register = template.Library()

@register.filter
def intdiv(value, arg):
    """Divide el valor entero por el argumento."""
    try:
        return int(value) // int(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def modulo(value, arg):
    """Calcula el módulo (resto) de dividir el valor por el argumento."""
    try:
        return int(value) % int(arg)
    except (ValueError, ZeroDivisionError):
        return 0