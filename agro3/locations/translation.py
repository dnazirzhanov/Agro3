from modeltranslation.translator import translator, TranslationOptions
from .models import Country, Region, City


class CountryTranslationOptions(TranslationOptions):
    fields = ('name',)


class RegionTranslationOptions(TranslationOptions):
    fields = ('name',)


class CityTranslationOptions(TranslationOptions):
    fields = ('name',)


translator.register(Country, CountryTranslationOptions)
translator.register(Region, RegionTranslationOptions)
translator.register(City, CityTranslationOptions)