from django.db import models
from django.urls import reverse
from django.utils import timezone


class Product(models.Model):
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
