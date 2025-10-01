from django.contrib import admin
from .models import Country, Region, City


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'regions_count']
    search_fields = ['name', 'code']
    ordering = ['name']
    
    def regions_count(self, obj):
        return obj.regions.count()
    regions_count.short_description = 'Regions'


class RegionInline(admin.TabularInline):
    model = Region
    extra = 0
    fields = ['name', 'type_name']


class CityInline(admin.TabularInline):
    model = City
    extra = 0
    fields = ['name', 'type_name']


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'type_name', 'cities_count']
    list_filter = ['country', 'type_name']
    search_fields = ['name', 'country__name']
    ordering = ['country__name', 'name']
    inlines = [CityInline]
    
    def cities_count(self, obj):
        return obj.cities.count()
    cities_count.short_description = 'Cities/Villages'


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'region', 'country_name', 'type_name']
    list_filter = ['region__country', 'region', 'type_name']
    search_fields = ['name', 'region__name', 'region__country__name']
    ordering = ['region__country__name', 'region__name', 'name']
    
    def country_name(self, obj):
        return obj.region.country.name
    country_name.short_description = 'Country'