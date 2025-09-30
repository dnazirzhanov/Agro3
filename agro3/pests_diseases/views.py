"""
Views for pest and disease information display and management.

This module handles HTTP requests for viewing pest and disease information,
filtering by type, and displaying identification and management guidance to
help farmers protect their crops.
"""
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import PestOrDisease


def pest_disease_list_view(request):
    """
    Display a list of all pests and diseases with filtering.
    
    Handles GET requests with optional filters:
    - type: Filter by pest or disease type
    - search: Search by name
    - page: Pagination (12 items per page)
    
    Returns:
        Paginated list of pests and diseases with applied filters
    """
    pests_diseases = PestOrDisease.objects.all()
    
    # Filter by type
    type_filter = request.GET.get('type')
    if type_filter:
        pests_diseases = pests_diseases.filter(type=type_filter)
    
    # Search by name
    search = request.GET.get('search')
    if search:
        pests_diseases = pests_diseases.filter(name__icontains=search)
    
    # Pagination
    paginator = Paginator(pests_diseases, 12)
    page_number = request.GET.get('page')
    pests_diseases = paginator.get_page(page_number)
    
    context = {
        'pests_diseases': pests_diseases,
        'type_choices': PestOrDisease.TYPE_CHOICES,
        'current_type': type_filter,
        'current_search': search or '',
    }
    
    return render(request, 'pests_diseases/list.html', context)


def pest_disease_detail_view(request, pk):
    """
    Display detailed information about a specific pest or disease.
    
    Handles GET requests to show comprehensive information including symptoms,
    identification tips, prevention methods, and management strategies.
    Also displays related pests or diseases of the same type.
    
    Args:
        pk: Primary key of the pest or disease to display
    
    Returns:
        Detailed pest/disease information page with management recommendations
    """
    pest_disease = get_object_or_404(PestOrDisease, pk=pk)
    
    # Get related pests/diseases of the same type
    related_items = PestOrDisease.objects.filter(type=pest_disease.type).exclude(pk=pest_disease.pk)[:4]
    
    context = {
        'pest_disease': pest_disease,
        'related_items': related_items,
    }
    
    return render(request, 'pests_diseases/detail.html', context)
