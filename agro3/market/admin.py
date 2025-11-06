from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import Product, Market, MarketPrice


@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    list_display = ['name', 'category', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'category', 'description']
    ordering = ['name']
    
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'category', 'description'),
            'description': 'Enter product details in multiple languages. English is required, Russian and Kyrgyz are optional.'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Market)
class MarketAdmin(TranslationAdmin):
    list_display = ['name', 'location', 'contact_info', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'location', 'contact_info']
    ordering = ['name']
    
    fieldsets = (
        ('Market Information', {
            'fields': ('name', 'description', 'location', 'contact_info'),
            'description': 'Enter market details in multiple languages. English is required, Russian and Kyrgyz are optional.'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(MarketPrice)
class MarketPriceAdmin(TranslationAdmin):
    list_display = ['product', 'market', 'price', 'unit', 'date_recorded']
    list_filter = ['product', 'market', 'unit', 'date_recorded', 'created_at']
    search_fields = ['product__name', 'market__name', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date_recorded'
    ordering = ['-date_recorded']
    
    fieldsets = (
        ('Price Information', {
            'fields': ('product', 'market', 'price', 'unit', 'date_recorded'),
            'description': 'Select product and market, then enter price details.'
        }),
        ('Additional Information (Multilingual)', {
            'fields': ('notes',),
            'description': 'Add notes in multiple languages. These notes will be displayed to users in their selected language.'
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
