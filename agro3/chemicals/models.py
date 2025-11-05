
from django.db import models

class ChemicalProduct(models.Model):
	name = models.CharField(max_length=200)
	description = models.TextField(blank=True, null=True)
	manufacturer = models.CharField(max_length=200, blank=True, null=True)
	active_ingredient = models.CharField(max_length=200, blank=True, null=True)
	registration_number = models.CharField(max_length=100, blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = 'Chemical Product'
		verbose_name_plural = 'Chemical Products'
		ordering = ['name']

	def __str__(self):
		return self.name
