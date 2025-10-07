from django.contrib import admin
from .models import ChemicalCategory, ChemicalProduct, Shop, ChemicalPrice, PriceHistory


@admin.register(ChemicalCategory)
class ChemicalCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_type', 'created_at')
    list_filter = ('category_type', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('category_type', 'name')


@admin.register(ChemicalProduct)
class ChemicalProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'package_size', 'package_unit', 'is_active')
    list_filter = ('category', 'brand', 'application_method', 'is_active', 'created_at')
    search_fields = ('name', 'brand', 'active_ingredient', 'target_crops')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'brand', 'is_active')
        }),
        ('Chemical Details', {
            'fields': ('active_ingredient', 'concentration', 'application_method')
        }),
        ('Packaging', {
            'fields': ('package_size', 'package_unit')
        }),
        ('Usage Information', {
            'fields': ('description', 'usage_instructions', 'dosage', 'target_crops', 'target_pests')
        }),
        ('Safety & Regulations', {
            'fields': ('safety_warnings', 'registration_number')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'shop_type', 'get_location_display', 'phone_number', 'whatsapp_number', 'is_active', 'is_verified')
    list_filter = ('shop_type', 'country', 'region', 'is_active', 'is_verified', 'delivery_available')
    search_fields = ('name', 'owner_name', 'phone_number', 'whatsapp_number', 'email', 'address')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'shop_type', 'owner_name', 'is_active', 'is_verified')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'whatsapp_number', 'email', 'website')
        }),
        ('Location', {
            'fields': ('country', 'region', 'city', 'address', 'google_maps_link')
        }),
        ('Business Details', {
            'fields': ('license_number', 'established_year', 'description')
        }),
        ('Delivery Information', {
            'fields': ('delivery_available', 'delivery_radius_km', 'working_hours')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


class PriceHistoryInline(admin.TabularInline):
    model = PriceHistory
    extra = 0
    readonly_fields = ('change_date', 'changed_by')


@admin.register(ChemicalPrice)
class ChemicalPriceAdmin(admin.ModelAdmin):
    list_display = ('product', 'shop', 'price', 'currency', 'is_in_stock', 'last_updated')
    list_filter = ('currency', 'is_in_stock', 'product__category', 'shop__shop_type', 'last_updated')
    search_fields = ('product__name', 'product__brand', 'shop__name')
    readonly_fields = ('last_updated',)
    inlines = [PriceHistoryInline]
    fieldsets = (
        ('Product & Shop', {
            'fields': ('product', 'shop')
        }),
        ('Pricing', {
            'fields': ('price', 'currency', 'discount_percentage', 'bulk_price_threshold', 'bulk_price')
        }),
        ('Availability', {
            'fields': ('is_in_stock', 'stock_quantity', 'minimum_order')
        }),
        ('Additional Information', {
            'fields': ('updated_by', 'notes', 'last_updated')
        })
    )

    def save_model(self, request, obj, form, change):
        # Automatically set the updated_by field to current user
        if not obj.updated_by:
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('chemical_price', 'old_price', 'new_price', 'get_change_percentage', 'change_date', 'changed_by')
    list_filter = ('change_date', 'chemical_price__product__category')
    search_fields = ('chemical_price__product__name', 'chemical_price__shop__name', 'reason')
    readonly_fields = ('change_date',)
    
    def get_change_percentage(self, obj):
        change = obj.get_change_percentage()
        return f"{change:.1f}%" if change else "0%"
    get_change_percentage.short_description = "Change %"
