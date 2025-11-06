from modeltranslation.translator import register, TranslationOptions
from .models import ChemicalProduct, ChemicalCategory, Shop


@register(ChemicalProduct)
class ChemicalProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'usage_instructions', 'target_crops', 'target_pests', 'safety_warnings', 'brand', 'active_ingredient')
    required_languages = ('en',)


@register(ChemicalCategory) 
class ChemicalCategoryTranslationOptions(TranslationOptions):
    fields = ('name', 'description')
    required_languages = ('en',)


@register(Shop)
class ShopTranslationOptions(TranslationOptions):
    fields = ('name', 'description')
    required_languages = ('en',)