from django.http import JsonResponse
from django.views.generic import View, TemplateView
from .models import Country, Region, City
from users.models import UserProfile


class GetRegionsView(View):
    """AJAX view to get regions for a selected country"""
    
    def get(self, request):
        country_id = request.GET.get('country_id')
        if country_id:
            regions = Region.objects.filter(country_id=country_id).order_by('name')
            data = [{'id': region.id, 'name': region.name} for region in regions]
            return JsonResponse({'regions': data})
        return JsonResponse({'regions': []})


class GetCitiesView(View):
    """AJAX view to get cities for a selected region"""
    
    def get(self, request):
        region_id = request.GET.get('region_id')
        if region_id:
            cities = City.objects.filter(region_id=region_id).order_by('name')
            data = [{'id': city.id, 'name': city.name, 'type': city.get_type_name_display()} for city in cities]
            return JsonResponse({'cities': data})
        return JsonResponse({'cities': []})


class SearchLocationsView(View):
    """AJAX view for location search/autocomplete"""
    
    def get(self, request):
        query = request.GET.get('q', '').strip()
        
        if len(query) < 2:
            return JsonResponse({'results': []})
        
        # Search in cities
        cities = City.objects.filter(
            name__icontains=query
        ).select_related('region__country')[:20]
        
        results = []
        for city in cities:
            results.append({
                'id': city.id,
                'text': f"{city.name}, {city.region.name}, {city.region.country.name}",
                'city_id': city.id,
                'region_id': city.region.id,
                'country_id': city.region.country.id,
            })
        
        return JsonResponse({'results': results})


class LocationSearchPageView(TemplateView):
    """View for location-based search page"""
    template_name = 'location_search.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all countries for dropdown
        context['countries'] = Country.objects.all().order_by('name')
        
        # Handle search if parameters are provided
        country_id = self.request.GET.get('country')
        region_id = self.request.GET.get('region')
        city_id = self.request.GET.get('city')
        
        if country_id or region_id or city_id:
            # Build query based on location parameters
            profiles = UserProfile.objects.select_related('user', 'country', 'region_new', 'city')
            
            if country_id:
                profiles = profiles.filter(country_id=country_id)
            if region_id:
                profiles = profiles.filter(region_new_id=region_id)
            if city_id:
                profiles = profiles.filter(city_id=city_id)
                
            context['search_results'] = profiles[:20]  # Limit results
            
        return context