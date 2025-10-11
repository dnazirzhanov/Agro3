"""
Translation configuration for market models.

This module defines which model fields should be translatable using
django-modeltranslation, enabling multi-language support for market
data including product names and descriptions.
"""
from modeltranslation.translator import register, TranslationOptions
from .models import Product, Market


@register(Product)
class ProductTranslationOptions(TranslationOptions):
    """Translation options for Product model."""
    fields = ('name', 'category', 'description')


@register(Market)
class MarketTranslationOptions(TranslationOptions):
    """Translation options for Market model."""
    fields = ('name', 'description')