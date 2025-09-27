from django.db import models
from django.urls import reverse


class SoilType(models.Model):
    TEXTURE_CHOICES = [
        ('Sandy', 'Sandy'),
        ('Loamy', 'Loamy'),
        ('Clay', 'Clay'),
        ('Silty', 'Silty'),
    ]
    
    DRAINAGE_CHOICES = [
        ('Good', 'Good'),
        ('Moderate', 'Moderate'),
        ('Poor', 'Poor'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    texture = models.CharField(max_length=20, choices=TEXTURE_CHOICES)
    drainage = models.CharField(max_length=20, choices=DRAINAGE_CHOICES)
    nutrient_retention = models.CharField(max_length=100)
    recommended_amendments = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('soil:detail', kwargs={'pk': self.pk})


class Crop(models.Model):
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
    soil_preference = models.ForeignKey(
        SoilType, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='preferred_crops'
    )
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
