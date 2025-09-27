from django.contrib import admin
from .models import Crop, SoilType


@admin.register(SoilType)
class SoilTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'texture', 'drainage', 'nutrient_retention']
    list_filter = ['texture', 'drainage']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ['name', 'scientific_name', 'sunlight_needs', 'water_needs', 'soil_preference', 'featured_image']
    list_filter = ['sunlight_needs', 'water_needs', 'soil_preference', 'created_at']
    search_fields = ['name', 'scientific_name', 'description']
    filter_horizontal = []  # For many-to-many fields if any
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'scientific_name', 'description', 'featured_image')
        }),
        ('Growing Requirements', {
            'fields': ('sunlight_needs', 'water_needs', 'soil_preference', 'climate_preference')
        }),
        ('Timeline & Care', {
            'fields': ('planting_seasons', 'harvest_time', 'nutrient_needs', 'recommended_usage')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    ordering = ['name']
