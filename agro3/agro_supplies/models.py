from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from locations.models import Country, Region, City
from decimal import Decimal


class ChemicalCategory(models.Model):
    """Categories for agricultural chemicals"""
    CATEGORY_CHOICES = [
        ('fertilizer', 'Fertilizers'),
        ('pesticide', 'Pesticides'),
        ('herbicide', 'Herbicides'),
        ('fungicide', 'Fungicides'),
        ('insecticide', 'Insecticides'),
        ('growth_regulator', 'Growth Regulators'),
        ('soil_conditioner', 'Soil Conditioners'),
    ]
    
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Bootstrap icon class")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Chemical Categories"
        ordering = ['category_type', 'name']
    
    def __str__(self):
        return f"{self.get_category_type_display()} - {self.name}"


class ChemicalProduct(models.Model):
    """Agricultural chemical products"""
    UNIT_CHOICES = [
        ('kg', 'Kilogram'),
        ('liter', 'Liter'),
        ('gram', 'Gram'),
        ('ml', 'Milliliter'),
        ('bag', 'Bag'),
        ('bottle', 'Bottle'),
        ('packet', 'Packet'),
    ]
    
    APPLICATION_CHOICES = [
        ('foliar', 'Foliar Application'),
        ('soil', 'Soil Application'),
        ('seed', 'Seed Treatment'),
        ('drip', 'Drip Irrigation'),
        ('spray', 'Spray Application'),
    ]
    
    name = models.CharField(max_length=200)
    category = models.ForeignKey(ChemicalCategory, on_delete=models.CASCADE, related_name='products')
    brand = models.CharField(max_length=100)
    active_ingredient = models.CharField(max_length=200, help_text="Main active chemical compounds")
    concentration = models.CharField(max_length=50, help_text="e.g., 20% EC, 80% WP")
    
    # Product details
    description = models.TextField()
    usage_instructions = models.TextField(help_text="How to use this product")
    dosage = models.CharField(max_length=200, help_text="Recommended dosage per hectare or liter")
    application_method = models.CharField(max_length=20, choices=APPLICATION_CHOICES)
    
    # Packaging
    package_size = models.DecimalField(max_digits=10, decimal_places=2)
    package_unit = models.CharField(max_length=20, choices=UNIT_CHOICES)
    
    # Safety and regulations
    safety_warnings = models.TextField(blank=True, help_text="Safety precautions and warnings")
    registration_number = models.CharField(max_length=100, blank=True, help_text="Government registration number")
    
    # Target crops/pests
    target_crops = models.TextField(help_text="Crops this product is suitable for")
    target_pests = models.TextField(blank=True, help_text="Pests/diseases this product treats")
    
    # Meta information
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['category', 'brand', 'name']
        unique_together = ['name', 'brand', 'package_size', 'package_unit']
    
    def __str__(self):
        return f"{self.brand} {self.name} ({self.package_size}{self.package_unit})"
    
    def get_absolute_url(self):
        return reverse('agro_supplies:product_detail', kwargs={'pk': self.pk})
    
    def is_liquid(self):
        """Determine if product is liquid based on unit and concentration"""
        liquid_units = ['liter', 'ml']
        liquid_indicators = ['EC', 'SL', 'SC', 'AS']  # Common liquid formulation codes
        
        # Check if unit indicates liquid
        if self.package_unit in liquid_units:
            return True
        
        # Check concentration for liquid indicators
        concentration_upper = self.concentration.upper()
        return any(indicator in concentration_upper for indicator in liquid_indicators)
    
    def get_standard_unit(self):
        """Get the standard unit for pricing (som per liter or som per kg)"""
        return "liter" if self.is_liquid() else "kg"
    
    def get_standard_unit_display(self):
        """Get display text for standard unit"""
        return "som/liter" if self.is_liquid() else "som/kg"


class Shop(models.Model):
    """Agricultural supply shops/vendors"""
    SHOP_TYPES = [
        ('retail', 'Retail Shop'),
        ('wholesale', 'Wholesale'),
        ('distributor', 'Distributor'),
        ('online', 'Online Store'),
        ('cooperative', 'Agricultural Cooperative'),
    ]
    
    name = models.CharField(max_length=200)
    shop_type = models.CharField(max_length=20, choices=SHOP_TYPES, default='retail')
    owner_name = models.CharField(max_length=100, blank=True)
    
    # Contact information
    phone_number = models.CharField(max_length=20)
    whatsapp_number = models.CharField(max_length=20, blank=True, help_text="WhatsApp contact number")
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    google_maps_link = models.URLField(blank=True, help_text="Google Maps link to shop location")
    
    # Location using hierarchical system
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='shops')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='shops', null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='shops', null=True, blank=True)
    address = models.TextField(help_text="Detailed address")
    
    # Business details
    license_number = models.CharField(max_length=100, blank=True)
    established_year = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    
    # Operating details
    working_hours = models.CharField(max_length=200, blank=True, help_text="e.g., Mon-Fri: 8AM-6PM")
    delivery_available = models.BooleanField(default=False)
    delivery_radius_km = models.IntegerField(null=True, blank=True, help_text="Delivery radius in kilometers")
    
    # Products they sell
    chemical_products = models.ManyToManyField(ChemicalProduct, through='ChemicalPrice', related_name='available_shops')
    
    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False, help_text="Verified by administrators")
    
    class Meta:
        ordering = ['country', 'region', 'city', 'name']
    
    def __str__(self):
        location = []
        if self.city:
            location.append(self.city.name)
        if self.region:
            location.append(self.region.name)
        if self.country:
            location.append(self.country.name)
        
        location_str = ", ".join(location) if location else "Unknown Location"
        return f"{self.name} ({location_str})"
    
    def get_absolute_url(self):
        return reverse('agro_supplies:shop_detail', kwargs={'pk': self.pk})
    
    def get_location_display(self):
        """Get formatted location string"""
        parts = []
        if self.city:
            parts.append(self.city.name)
        if self.region:
            parts.append(self.region.name)
        parts.append(self.country.name)
        return ", ".join(parts)


class ChemicalPrice(models.Model):
    """Current prices of chemical products in different shops"""
    product = models.ForeignKey(ChemicalProduct, on_delete=models.CASCADE, related_name='prices')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='product_prices')
    
    # Price information
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in local currency")
    currency = models.CharField(max_length=10, default='KGS', help_text="Currency code (KGS, USD, etc.)")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Discount percentage if any")
    
    # Availability
    is_in_stock = models.BooleanField(default=True)
    stock_quantity = models.IntegerField(null=True, blank=True, help_text="Available quantity")
    minimum_order = models.IntegerField(default=1, help_text="Minimum order quantity")
    
    # Pricing details
    bulk_price_threshold = models.IntegerField(null=True, blank=True, help_text="Minimum quantity for bulk pricing")
    bulk_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Price for bulk orders")
    
    # Metadata
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, help_text="Who last updated this price")
    notes = models.TextField(blank=True, help_text="Additional notes about pricing or availability")
    
    class Meta:
        unique_together = ['product', 'shop']
        ordering = ['product', 'price']
    
    def __str__(self):
        return f"{self.product.name} at {self.shop.name} - {self.price} {self.currency}"
    
    def get_effective_price(self):
        """Get price after discount"""
        if self.discount_percentage > 0:
            discount_amount = self.price * (self.discount_percentage / 100)
            return self.price - discount_amount
        return self.price
    
    def get_bulk_savings(self):
        """Calculate savings with bulk pricing"""
        if self.bulk_price and self.bulk_price < self.price:
            return self.price - self.bulk_price
        return Decimal('0.00')
    
    def get_standardized_price(self):
        """Get price per standard unit (som per liter for liquids, som per kg for solids)"""
        effective_price = self.get_effective_price()
        package_size = self.product.package_size
        package_unit = self.product.package_unit
        
        # Convert package size to standard unit
        if self.product.is_liquid():
            # Convert to liters
            if package_unit == 'ml':
                standard_size = package_size / 1000
            elif package_unit == 'liter':
                standard_size = package_size
            else:
                # Assume 1 bottle/packet = package_size liters for liquids
                standard_size = package_size
        else:
            # Convert to kg
            if package_unit == 'gram':
                standard_size = package_size / 1000
            elif package_unit == 'kg':
                standard_size = package_size
            else:
                # Assume 1 bag/packet = package_size kg for solids
                standard_size = package_size
        
        # Calculate price per standard unit
        if standard_size > 0:
            return effective_price / standard_size
        return effective_price
    
    def get_standardized_price_display(self):
        """Get formatted standardized price with currency and unit"""
        price = self.get_standardized_price()
        unit = self.product.get_standard_unit_display()
        return f"{price:.2f} {unit}"


class PriceHistory(models.Model):
    """Historical price tracking for analysis"""
    chemical_price = models.ForeignKey(ChemicalPrice, on_delete=models.CASCADE, related_name='history')
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    change_date = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.CharField(max_length=200, blank=True, help_text="Reason for price change")
    
    class Meta:
        ordering = ['-change_date']
        verbose_name_plural = "Price Histories"
    
    def __str__(self):
        return f"{self.chemical_price.product.name} price change: {self.old_price} → {self.new_price}"
    
    def get_change_percentage(self):
        """Calculate percentage change"""
        if self.old_price > 0:
            return ((self.new_price - self.old_price) / self.old_price) * 100
        return 0
