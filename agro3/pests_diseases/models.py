from django.db import models
from django.urls import reverse
from crops.models import Crop


class PestOrDisease(models.Model):
    TYPE_CHOICES = [
        ('Pest', 'Pest'),
        ('Disease', 'Disease'),
    ]
    
    name = models.CharField(max_length=200)
    scientific_name = models.CharField(max_length=250, blank=True, null=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    symptoms = models.TextField()
    causes = models.TextField(blank=True, null=True)
    identification_tips = models.TextField(blank=True, null=True)
    prevention_methods = models.TextField(blank=True, null=True)
    management_strategies = models.TextField(blank=True, null=True)
    affected_crops = models.ManyToManyField(
        Crop,
        related_name='affected_by',
        blank=True
    )
    featured_image = models.ImageField(upload_to='pests_diseases/featured/', blank=True, null=True)
    example_images = models.ImageField(upload_to='pests_diseases/examples/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Pest or Disease'
        verbose_name_plural = 'Pests and Diseases'
    
    def __str__(self):
        return f"{self.name} ({self.type})"
    
    def get_absolute_url(self):
        return reverse('pests_diseases:detail', kwargs={'pk': self.pk})
