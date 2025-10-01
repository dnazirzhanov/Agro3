"""
Views for crop and soil type information display and filtering.

This module handles HTTP requests for viewing crop information, filtering crops
by various criteria, and displaying detailed crop characteristics to help farmers
make informed planting decisions.
"""
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Crop, SoilType


def crop_list_view(request):
    """
    Display a list of all crops with pagination and filtering.
    
    Handles GET requests to display crops with optional filters:
    - sunlight: Filter by sunlight requirements (Full Sun, Partial Shade, Full Shade)
    - water: Filter by water requirements (Low, Medium, High)
    - search: Search crops by name
    
    Returns:
        Paginated list of crops (12 per page) with applied filters
    """
    crops = Crop.objects.all()
    
    # Filter by sunlight needs if provided
    sunlight_filter = request.GET.get('sunlight')
    if sunlight_filter:
        crops = crops.filter(sunlight_needs=sunlight_filter)
    
    # Filter by water needs if provided
    water_filter = request.GET.get('water')
    if water_filter:
        crops = crops.filter(water_needs=water_filter)
    
    # Search by name
    search = request.GET.get('search')
    if search:
        crops = crops.filter(name__icontains=search)
    
    # Pagination
    paginator = Paginator(crops, 12)  # Show 12 crops per page
    page_number = request.GET.get('page')
    crops = paginator.get_page(page_number)
    
    # Get filter choices for the template
    sunlight_choices = Crop.SUNLIGHT_CHOICES
    water_choices = Crop.WATER_CHOICES
    
    context = {
        'crops': crops,
        'sunlight_choices': sunlight_choices,
        'water_choices': water_choices,
        'current_sunlight': sunlight_filter,
        'current_water': water_filter,
        'current_search': search or '',
    }
    
    return render(request, 'crops/crop_list.html', context)


def crop_detail_view(request, pk):
    """
    Display detailed information about a specific crop.
    
    Handles GET requests to show comprehensive crop information including
    growing requirements, planting seasons, harvest times, and nutrient needs.
    Also displays related crops with similar characteristics.
    
    Args:
        pk: Primary key of the crop to display
    
    Returns:
        Detailed crop information page with related crop recommendations
    """
    crop = get_object_or_404(Crop, pk=pk)
    
    # Get related crops with similar characteristics
    related_crops = Crop.objects.filter(
        sunlight_needs=crop.sunlight_needs,
        water_needs=crop.water_needs
    ).exclude(pk=crop.pk)[:4]
    
    context = {
        'crop': crop,
        'related_crops': related_crops,
    }
    
    return render(request, 'crops/crop_detail.html', context)
