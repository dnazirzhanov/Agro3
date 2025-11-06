"""
Views for chemical products listing and management.

This module handles HTTP requests for displaying chemical products with
multilingual support, filtering products based on user's language choice,
and providing search/filter functionality.
"""
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.translation import get_language, gettext_lazy as _
from agro_supplies.models import ChemicalProduct


def filter_by_language(queryset, language_code):
    """
    Filter queryset to only include chemical products that have translations 
    in the specified language.
    """
    if language_code == 'en':
        # English is the default language, always show all objects
        return queryset
    
    # For non-English languages, filter products that have translation
    field_name = f'name_{language_code}'
    return queryset.filter(**{f'{field_name}__isnull': False}).exclude(**{field_name: ''})


def chemicals_list_view(request):
    """
    Display chemical products with filtering and search capabilities.
    
    Only shows products that have translations in the user's chosen language.
    This ensures users only see content they can understand.
    
    Handles GET requests with optional filters:
    - search: Search products by name, manufacturer, or active ingredient
    - manufacturer: Filter by manufacturer
    - category: Filter by category (if added later)
    - page: Pagination (20 products per page)
    """
    current_language = get_language() or 'en'
    
    # Get all chemical products with translations in user's language
    available_products = filter_by_language(ChemicalProduct.objects.all(), current_language)
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        if current_language == 'en':
            available_products = available_products.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(brand__icontains=search) |
                Q(active_ingredient__icontains=search)
            )
        else:
            # Search in translated fields
            search_filter = (
                Q(**{f'name_{current_language}__icontains': search}) |
                Q(**{f'description_{current_language}__icontains': search}) |
                Q(**{f'brand_{current_language}__icontains': search}) |
                Q(**{f'active_ingredient_{current_language}__icontains': search})
            )
            available_products = available_products.filter(search_filter)
    
    # Manufacturer/Brand filter  
    manufacturer_filter = request.GET.get('manufacturer')
    if manufacturer_filter:
        if current_language == 'en':
            available_products = available_products.filter(brand__icontains=manufacturer_filter)
        else:
            available_products = available_products.filter(**{f'brand_{current_language}__icontains': manufacturer_filter})
    
    # Get unique manufacturers/brands for filter dropdown (in user's language)
    if current_language == 'en':
        manufacturers = ChemicalProduct.objects.exclude(brand__isnull=True).exclude(brand='').values_list('brand', flat=True).distinct()
    else:
        field_name = f'brand_{current_language}'
        manufacturers = ChemicalProduct.objects.exclude(**{f'{field_name}__isnull': True}).exclude(**{field_name: ''}).values_list(field_name, flat=True).distinct()
    
    manufacturers = [m for m in manufacturers if m] # Remove empty values
    
    # Pagination
    paginator = Paginator(available_products, 20)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    
    context = {
        'products': products,
        'manufacturers': sorted(manufacturers),
        'current_search': search or '',
        'current_manufacturer': manufacturer_filter or '',
        'current_language': current_language,
    }
    
    return render(request, 'chemicals/chemicals_list.html', context)
