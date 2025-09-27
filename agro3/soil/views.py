from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from crops.models import SoilType


def soil_type_questionnaire_view(request):
    """Multi-step questionnaire for soil type identification."""
    if request.method == 'POST':
        # Process questionnaire responses
        texture = request.POST.get('texture')
        drainage = request.POST.get('drainage')
        stickiness = request.POST.get('stickiness')
        color = request.POST.get('color')
        
        # Simple soil type determination logic
        identified_soil = identify_soil_type(texture, drainage, stickiness, color)
        
        if identified_soil:
            request.session['identified_soil_id'] = identified_soil.pk
            return redirect('soil:result')
        else:
            messages.error(request, 'Could not determine soil type based on your answers. Please try again or consult an expert.')
    
    # Get all soil types for reference
    soil_types = SoilType.objects.all()
    
    context = {
        'soil_types': soil_types,
    }
    
    return render(request, 'soil/questionnaire.html', context)


def soil_type_result_view(request):
    """Display the identified soil type and recommendations."""
    soil_id = request.session.get('identified_soil_id')
    
    if not soil_id:
        messages.error(request, 'No soil identification found. Please take the questionnaire first.')
        return redirect('soil:questionnaire')
    
    soil_type = get_object_or_404(SoilType, pk=soil_id)
    
    # Clear the session
    if 'identified_soil_id' in request.session:
        del request.session['identified_soil_id']
    
    # Get suitable crops for this soil type
    suitable_crops = soil_type.preferred_crops.all()[:6]
    
    context = {
        'soil_type': soil_type,
        'suitable_crops': suitable_crops,
    }
    
    return render(request, 'soil/result.html', context)


def soil_type_list_view(request):
    """Display all available soil types."""
    soil_types = SoilType.objects.all()
    
    context = {
        'soil_types': soil_types,
    }
    
    return render(request, 'soil/list.html', context)


def soil_type_detail_view(request, pk):
    """Display detailed information about a specific soil type."""
    soil_type = get_object_or_404(SoilType, pk=pk)
    suitable_crops = soil_type.preferred_crops.all()
    
    context = {
        'soil_type': soil_type,
        'suitable_crops': suitable_crops,
    }
    
    return render(request, 'soil/detail.html', context)


def identify_soil_type(texture, drainage, stickiness, color):
    """
    Simple soil type identification based on questionnaire responses.
    In a real application, this would use more sophisticated algorithms.
    """
    # Simple rule-based identification
    if texture == 'sandy':
        if drainage == 'good':
            return SoilType.objects.filter(texture='Sandy').first()
    elif texture == 'sticky' and stickiness == 'very_sticky':
        return SoilType.objects.filter(texture='Clay').first()
    elif texture == 'smooth' and stickiness == 'slightly_sticky':
        return SoilType.objects.filter(texture='Silty').first()
    elif texture == 'mixed':
        return SoilType.objects.filter(texture='Loamy').first()
    
    # If no specific match, return the most common soil type
    return SoilType.objects.first()
