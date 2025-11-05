from modeltranslation.translator import register, TranslationOptions
from .models import Statistic


@register(Statistic)
class StatisticTranslationOptions(TranslationOptions):
    fields = ('title', 'short_description')
    required_languages = ('en',)