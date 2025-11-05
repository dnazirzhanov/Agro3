from django import template
from django.utils.translation import get_language
register = template.Library()

@register.filter
def get_translated(obj, field):
    lang = get_language() or 'en'
    val = getattr(obj, f"{field}_{lang}", None)
    if val:
        return val
    # fallback to default
    return getattr(obj, field, '')
