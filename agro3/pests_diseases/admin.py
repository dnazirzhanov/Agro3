from django.contrib import admin
from .models import PestOrDisease


@admin.register(PestOrDisease)
class PestOrDiseaseAdmin(admin.ModelAdmin):
    list_display = ['name', 'scientific_name', 'type', 'featured_image', 'created_at']
    list_filter = ['type', 'created_at', 'affected_crops']
    search_fields = ['name', 'scientific_name', 'symptoms']
    filter_horizontal = ['affected_crops']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'scientific_name', 'type')
        }),
        ('Identification', {
            'fields': ('symptoms', 'identification_tips', 'featured_image', 'example_images')
        }),
        ('Management', {
            'fields': ('causes', 'prevention_methods', 'management_strategies')
        }),
        ('Affected Crops', {
            'fields': ('affected_crops',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    ordering = ['name']
