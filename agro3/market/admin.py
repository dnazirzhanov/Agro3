from django.contrib import admin
from .models import Product, Market, MarketPrice


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'category', 'description']
    ordering = ['name']


@admin.register(Market)
class MarketAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'contact_info', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'location', 'contact_info']
    ordering = ['name']


@admin.register(MarketPrice)
class MarketPriceAdmin(admin.ModelAdmin):
    list_display = ['product', 'market', 'price', 'unit', 'date_recorded']
    list_filter = ['product', 'market', 'unit', 'date_recorded', 'created_at']
    search_fields = ['product__name', 'market__name', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date_recorded'
    ordering = ['-date_recorded']
    
    fieldsets = (
        ('Price Information', {
            'fields': ('product', 'market', 'price', 'unit', 'date_recorded')
        }),
        ('Additional Info', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
