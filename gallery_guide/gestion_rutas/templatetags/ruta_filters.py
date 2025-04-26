from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Devuelve un elemento de un diccionario o lista usando una clave o índice"""
    if dictionary is None:
        return None
    
    try:
        if isinstance(dictionary, dict):
            return dictionary.get(key)
        elif isinstance(dictionary, (list, tuple)) and isinstance(key, int):
            if 0 <= key < len(dictionary):
                return dictionary[key]
        return None
    except (KeyError, IndexError, TypeError):
        return None

@register.filter
def attr(obj, attr_name):
    """Accede a un atributo de un objeto por su nombre"""
    if obj is None:
        return None
    
    try:
        return getattr(obj, attr_name)
    except (AttributeError, TypeError):
        return None