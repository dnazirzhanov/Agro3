"""
Models for crop management in the agricultural application.

This module contains models representing different types of crops,
including their characteristics and growing requirements.
"""
from django.db import models
from django.urls import reverse


class Crop(models.Model):
    """
    Represents agricultural crops with detailed growing requirements and characteristics.
    
    Stores information about various crops including their sunlight needs, water requirements,
    preferred soil type, planting seasons, and harvest times. Used for crop recommendation
    and agricultural planning.
    """
    SUNLIGHT_CHOICES = [
        ('Full Sun', 'Full Sun'),
        ('Partial Shade', 'Partial Shade'),
        ('Full Shade', 'Full Shade'),
    ]
    
    WATER_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    
    name = models.CharField(max_length=100)
    scientific_name = models.CharField(max_length=150, blank=True, null=True)
    description = models.TextField()
    sunlight_needs = models.CharField(max_length=20, choices=SUNLIGHT_CHOICES)
    water_needs = models.CharField(max_length=20, choices=WATER_CHOICES)
    climate_preference = models.CharField(max_length=200)
    planting_seasons = models.TextField(blank=True, null=True)
    harvest_time = models.CharField(max_length=100, blank=True, null=True)
    nutrient_needs = models.TextField(blank=True, null=True)
    recommended_usage = models.TextField(blank=True, null=True)
    featured_image = models.ImageField(upload_to='crops/images/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('crops:detail', kwargs={'pk': self.pk})
