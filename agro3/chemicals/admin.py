from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from modeltranslation.admin import TranslationAdmin
from .models import ChemicalProduct

@admin.register(ChemicalProduct)
class ChemicalProductAdmin(TranslationAdmin):
    list_display = ('name', 'manufacturer', 'active_ingredient', 'registration_number', 'created_at')
    search_fields = ('name', 'manufacturer', 'active_ingredient', 'registration_number')
    list_filter = ('created_at', 'updated_at')
    ordering = ['name']
    
    fieldsets = (
        ('Chemical Product Information', {
            'fields': ('name', 'description', 'manufacturer', 'active_ingredient'),
            'description': 'Enter product details in multiple languages. English is required, Russian and Kyrgyz are optional.'
        }),
        ('Registration Details', {
            'fields': ('registration_number',),
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ('created_at', 'updated_at')
