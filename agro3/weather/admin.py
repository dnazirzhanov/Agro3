from django.contrib import admin
from .models import WeatherLocation, WeatherData


@admin.register(WeatherLocation)
class WeatherLocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'state', 'latitude', 'longitude', 'created_at']
    list_filter = ['country', 'created_at']
    search_fields = ['name', 'country', 'state']
    readonly_fields = ['created_at']


@admin.register(WeatherData)
class WeatherDataAdmin(admin.ModelAdmin):
    list_display = ['location', 'timestamp', 'temperature', 'weather_main', 'humidity', 'wind_speed', 'created_at']
    list_filter = ['weather_main', 'location', 'timestamp', 'created_at']
    search_fields = ['location__name', 'weather_description']
    readonly_fields = ['created_at']
    date_hierarchy = 'timestamp'