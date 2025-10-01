from django.db import models
from django.utils import timezone


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=3, unique=True, help_text="ISO country code (e.g., KG, US, RU)")
    
    class Meta:
        verbose_name_plural = "Countries"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Region(models.Model):
    """States, Oblasts, Provinces, etc."""
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='regions')
    name = models.CharField(max_length=100)
    type_name = models.CharField(max_length=20, default='Region', help_text="e.g., State, Oblast, Province")
    
    class Meta:
        unique_together = ['country', 'name']
        ordering = ['country__name', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.country.name})"


class City(models.Model):
    """Cities, Towns, Villages"""
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='cities')
    name = models.CharField(max_length=100)
    type_name = models.CharField(
        max_length=20, 
        choices=[
            ('city', 'City'),
            ('town', 'Town'),
            ('village', 'Village'),
            ('district', 'District'),
            ('settlement', 'Settlement'),
        ],
        default='city'
    )
    
    class Meta:
        verbose_name_plural = "Cities"
        unique_together = ['region', 'name']
        ordering = ['region__country__name', 'region__name', 'name']
    
    def __str__(self):
        return f"{self.name}, {self.region.name}, {self.region.country.name}"