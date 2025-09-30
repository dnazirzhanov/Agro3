from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import PestOrDisease


def pest_disease_list_view(request):
    """Display a list of all pests and diseases with filtering."""
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
    """Display detailed information about a specific pest or disease."""
    pest_disease = get_object_or_404(PestOrDisease, pk=pk)
    
    # Get related pests/diseases of the same type
    related_items = PestOrDisease.objects.filter(type=pest_disease.type).exclude(pk=pest_disease.pk)[:4]
    
    context = {
        'pest_disease': pest_disease,
        'related_items': related_items,
    }
    
    return render(request, 'pests_diseases/detail.html', context)


def dose_calculator_view(request):
    """Chemical dose calculator for farmers."""
    result = None
    
    if request.method == 'POST':
        try:
            dose_per_liter = float(request.POST.get('dose_per_liter', 0))
            total_liters = float(request.POST.get('total_liters', 0))
            
            if dose_per_liter > 0 and total_liters > 0:
                total_dose = dose_per_liter * total_liters
                result = {
                    'dose_per_liter': dose_per_liter,
                    'total_liters': total_liters,
                    'total_dose': total_dose,
                    'total_dose_kg': total_dose / 1000
                }
        except (ValueError, TypeError):
            result = {'error': 'Please enter valid numbers'}
    
    return render(request, 'pests_diseases/dose_calculator.html', {'result': result})
