"""
Views for soil type identification and recommendations.

This module handles HTTP requests for soil type questionnaires, identification
results, and soil information display. Helps farmers identify their soil type
and get crop recommendations based on soil characteristics.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from crops.models import SoilType


def soil_type_questionnaire_view(request):
    """
    Multi-step questionnaire for soil type identification.
    
    Handles GET requests to display the questionnaire form and POST requests
    to process answers and identify soil type.
    
    POST parameters:
        texture: Soil texture (sandy, sticky, smooth, mixed)
        drainage: Drainage characteristics (good, moderate, poor)
        stickiness: Stickiness level (very_sticky, slightly_sticky, not_sticky)
        color: Soil color observation
    
    Returns:
        GET: Soil identification questionnaire form
        POST: Redirects to result page with identified soil type
    """
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
    """
    Display the identified soil type and recommendations.
    
    Handles GET requests to show soil identification results from the questionnaire.
    Retrieves soil type from session and displays characteristics, suitable crops,
    and improvement recommendations.
    
    Returns:
        Soil identification results with suitable crop recommendations
        Redirects to questionnaire if no identification found in session
    """
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
    """
    Display all available soil types.
    
    Handles GET requests to show a list of all soil types in the system
    for reference and educational purposes.
    
    Returns:
        List of all soil types with basic information
    """
    soil_types = SoilType.objects.all()
    
    context = {
        'soil_types': soil_types,
    }
    
    return render(request, 'soil/list.html', context)


def soil_type_detail_view(request, pk):
    """
    Display detailed information about a specific soil type.
    
    Handles GET requests to show comprehensive soil type information including
    characteristics, drainage properties, nutrient retention, and suitable crops.
    
    Args:
        pk: Primary key of the soil type to display
    
    Returns:
        Detailed soil type information page with crop recommendations
    """
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
    
    Uses rule-based logic to match questionnaire answers to soil types in the database.
    In a production application, this could use more sophisticated algorithms or
    machine learning models for better accuracy.
    
    Args:
        texture: Soil texture response (sandy, sticky, smooth, mixed)
        drainage: Drainage response (good, moderate, poor)
        stickiness: Stickiness response (very_sticky, slightly_sticky, not_sticky)
        color: Soil color response
    
    Returns:
        SoilType object that best matches the responses, or the most common
        soil type if no specific match is found
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
