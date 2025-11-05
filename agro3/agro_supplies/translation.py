from modeltranslation.translator import register, TranslationOptions
from .models import ChemicalProduct


@register(ChemicalProduct)
class ChemicalProductTranslationOptions(TranslationOptions):
    fields = ('name', 'description', 'usage_instructions', 'target_crops', 'target_pests', 'safety_warnings')
    required_languages = ('en',)