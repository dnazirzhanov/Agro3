"""
Translation configuration for chemical products models.

This module defines which model fields should be translatable using
django-modeltranslation, enabling multi-language support for chemical
product data including names, descriptions, and manufacturer information.
"""
from modeltranslation.translator import register, TranslationOptions
from .models import ChemicalProduct

@register(ChemicalProduct)
class ChemicalProductTranslationOptions(TranslationOptions):
    """Translation options for ChemicalProduct model."""
    fields = ('name', 'description', 'manufacturer', 'active_ingredient')
    required_languages = ('en',)
