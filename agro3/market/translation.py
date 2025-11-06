"""
Translation configuration for market models.

This module defines which model fields should be translatable using
django-modeltranslation, enabling multi-language support for market
data including product names, descriptions, and price notes.
"""
from modeltranslation.translator import register, TranslationOptions
from .models import Product, Market, MarketPrice


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    """Translation options for Product model."""
    fields = ('name', 'category', 'description')


@register(Market)
class MarketTranslationOptions(TranslationOptions):
    """Translation options for Market model."""
    fields = ('name', 'description')


@register(MarketPrice)
class MarketPriceTranslationOptions(TranslationOptions):
    """Translation options for MarketPrice model."""
    fields = ('notes',)