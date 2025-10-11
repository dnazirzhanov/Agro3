"""
Models for market price tracking and agricultural product management.

This module provides models for tracking agricultural product prices across
different markets, enabling farmers to make informed decisions about where
and when to sell their produce.
"""
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Product(models.Model):
    """
    Represents an agricultural product available in markets.
    
    Stores information about agricultural products such as crops, livestock,
    or farm supplies that are traded in various markets. Used for price tracking
    and market comparison.
    """
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Market(models.Model):
    """
    Represents a physical marketplace where agricultural products are sold.
    
    Contains information about markets in the Batken region including location,
    contact details, and operating hours. Used for organizing price data by
    geographical location.
    """
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    contact_info = models.CharField(max_length=200, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.location}"
    
    def get_absolute_url(self):
        return reverse('market:market_detail', kwargs={'pk': self.pk})


class MarketPrice(models.Model):
    """
    Represents the price of a product at a specific market on a specific date.
    
    Tracks historical and current prices of agricultural products across different
    markets. Enables price comparison, trend analysis, and helps farmers find the
    best prices for their products.
    """
    UNIT_CHOICES = [
        ('kg', 'Kilogram'),
        ('piece', 'Piece'),
        ('bundle', 'Bundle'),
        ('liter', 'Liter'),
        ('ton', 'Ton'),
        ('box', 'Box'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='prices')
    market = models.ForeignKey(Market, on_delete=models.CASCADE, related_name='prices')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='kg')
    date_recorded = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_recorded']
        unique_together = ['product', 'market', 'date_recorded']
    
    def __str__(self):
        return f"{self.product.name} - {self.market.name} - {self.price} som/{self.unit}"
    
    def get_absolute_url(self):
        return reverse('market:price_detail', kwargs={'pk': self.pk})
    
    def get_localized_price_display(self, language_code='en'):
        """Get price with localized currency and unit"""
        # Get localized currency
        if language_code == 'ky':
            currency_text = 'сом'
        elif language_code == 'ru':
            currency_text = 'сом'
        else:
            currency_text = 'som'
        
        # Get localized unit
        unit_translations = {
            'kg': {'ky': 'кг', 'ru': 'кг', 'en': 'kg'},
            'piece': {'ky': 'дн', 'ru': 'шт', 'en': 'pcs'},
            'bundle': {'ky': 'боо', 'ru': 'пуч', 'en': 'bundle'},
            'liter': {'ky': 'л', 'ru': 'л', 'en': 'L'},
            'ton': {'ky': 'т', 'ru': 'т', 'en': 't'},
            'box': {'ky': 'кут', 'ru': 'кор', 'en': 'box'},
        }
        
        unit_text = unit_translations.get(str(self.unit), {}).get(language_code, str(self.unit))
        return f"{self.price} {currency_text}/{unit_text}"
