# Dans ton template principal, ajoute ce filtre pour events_by_day|get_item:day
from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Retourne dictionary[key] ou [] si la clé est absente. Utilisé dans les templates pour accéder à un dict par variable."""
    return dictionary.get(key, [])
