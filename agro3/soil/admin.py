from django.contrib import admin
from crops.models import SoilType  # SoilType is defined in crops app

# SoilType is already registered in crops/admin.py
# If you want soil-specific admin, you can create proxy models or additional admin views
