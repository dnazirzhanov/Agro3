from django import template
from django.utils.translation import get_language

register = template.Library()

@register.filter
def localized_price(price_obj):
    """Return localized price display based on current language"""
    if hasattr(price_obj, 'get_localized_price_display'):
        current_language = get_language()
        return price_obj.get_localized_price_display(current_language)
    return str(price_obj)

@register.filter
def localized_currency(value):
    """Return localized currency symbol based on current language"""
    current_language = get_language()
    if current_language == 'ky':
        return 'сом'
    elif current_language == 'ru':
        return 'сом'
    return 'som'