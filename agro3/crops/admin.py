from django.contrib import admin
from .models import Crop


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ['name', 'scientific_name', 'sunlight_needs', 'water_needs', 'featured_image']
    list_filter = ['sunlight_needs', 'water_needs', 'created_at']
    search_fields = ['name', 'scientific_name', 'description']
    filter_horizontal = []  # For many-to-many fields if any
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'scientific_name', 'description', 'featured_image')
        }),
        ('Growing Requirements', {
            'fields': ('sunlight_needs', 'water_needs', 'climate_preference')
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
