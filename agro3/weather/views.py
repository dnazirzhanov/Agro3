"""
Views for weather information and forecasting.

This module handles HTTP requests for weather data retrieval, location search,
and weather dashboard display. Integrates with OpenWeatherMap API to provide
current weather and forecasts for agricultural planning.
"""
import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta
from .models import WeatherLocation, WeatherData
from locations.models import Country, Region, City
import os


def get_openweather_api_key():
    """
    Get OpenWeatherMap API key from environment or settings.
    
    Returns:
        API key string or None if not configured
    """
    return os.getenv('OPENWEATHER_API_KEY') or getattr(settings, 'OPENWEATHER_API_KEY', None)


def fetch_weather_data(lat, lon, location_name=None):
    """
    Fetch weather data from OpenWeatherMap API.
    
    Retrieves current weather and 24-hour forecast data for specified coordinates.
    Caches the data in the database to reduce API calls and improve performance.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        location_name: Optional location name for display
    
    Returns:
        Tuple of (weather_data_dict, error_message) where:
        - weather_data_dict contains 'current', 'forecast', and 'location' keys
        - error_message is None on success or contains error description on failure
    """
    api_key = get_openweather_api_key()
    if not api_key:
        return None, "Weather API key not configured. Please set OPENWEATHER_API_KEY environment variable."
    
    try:
        # Get current weather and forecast
        base_url = "http://api.openweathermap.org/data/2.5"
        
        # Current weather
        current_url = f"{base_url}/weather"
        current_params = {
            'lat': lat,
            'lon': lon,
            'appid': api_key,
            'units': 'metric'
        }
        
        # Hourly forecast (48 hours)
        forecast_url = f"{base_url}/forecast"
        forecast_params = {
            'lat': lat,
            'lon': lon,
            'appid': api_key,
            'units': 'metric'
        }
        
        current_response = requests.get(current_url, params=current_params, timeout=10)
        forecast_response = requests.get(forecast_url, params=forecast_params, timeout=10)
        
        if current_response.status_code == 200 and forecast_response.status_code == 200:
            current_data = current_response.json()
            forecast_data = forecast_response.json()
            
            # Get or create location
            location, created = WeatherLocation.objects.get_or_create(
                latitude=lat,
                longitude=lon,
                defaults={
                    'name': location_name or current_data.get('name', 'Unknown'),
                    'country': current_data.get('sys', {}).get('country', ''),
                }
            )
            
            # Save current weather
            current_weather = WeatherData.objects.update_or_create(
                location=location,
                timestamp=timezone.now().replace(minute=0, second=0, microsecond=0),
                defaults={
                    'temperature': current_data['main']['temp'],
                    'feels_like': current_data['main']['feels_like'],
                    'humidity': current_data['main']['humidity'],
                    'pressure': current_data['main']['pressure'],
                    'wind_speed': current_data.get('wind', {}).get('speed', 0),
                    'wind_direction': current_data.get('wind', {}).get('deg', 0),
                    'weather_main': current_data['weather'][0]['main'],
                    'weather_description': current_data['weather'][0]['description'],
                    'weather_icon': current_data['weather'][0]['icon'],
                    'visibility': current_data.get('visibility', 0),
                }
            )[0]
            
            # Save forecast data (next 24 hours)
            forecast_list = []
            for item in forecast_data['list'][:8]:  # Next 24 hours (3-hour intervals)
                timestamp = datetime.fromtimestamp(item['dt'], tz=timezone.get_current_timezone())
                weather, created = WeatherData.objects.update_or_create(
                    location=location,
                    timestamp=timestamp,
                    defaults={
                        'temperature': item['main']['temp'],
                        'feels_like': item['main']['feels_like'],
                        'humidity': item['main']['humidity'],
                        'pressure': item['main']['pressure'],
                        'wind_speed': item.get('wind', {}).get('speed', 0),
                        'wind_direction': item.get('wind', {}).get('deg', 0),
                        'weather_main': item['weather'][0]['main'],
                        'weather_description': item['weather'][0]['description'],
                        'weather_icon': item['weather'][0]['icon'],
                        'visibility': item.get('visibility', 0),
                    }
                )
                forecast_list.append(weather)
            
            return {
                'current': current_weather,
                'forecast': forecast_list,
                'location': location
            }, None
            
        else:
            return None, f"Weather API error: {current_response.status_code}"
            
    except requests.RequestException as e:
        return None, f"Failed to fetch weather data: {str(e)}"
    except Exception as e:
        return None, f"Weather data processing error: {str(e)}"


def weather_dashboard_view(request):
    """
    Main weather dashboard with location search.
    
    Handles GET requests to display weather information for a location.
    Uses cached data when available (less than 30 minutes old) to reduce API calls.
    Defaults to Batken, Kyrgyzstan if no location specified.
    
    GET parameters:
        lat: Latitude coordinate
        lon: Longitude coordinate
        location: Location name for display
    
    Returns:
        Weather dashboard page with current weather, forecast, and
        agricultural recommendations based on weather conditions
    """
    # Default location (Batken, Kyrgyzstan)
    default_lat, default_lon = 40.0628, 70.8175
    default_name = "Batken"
    
    # Get location from request
    lat = request.GET.get('lat', default_lat)
    lon = request.GET.get('lon', default_lon)
    location_name = request.GET.get('location', default_name)
    
    try:
        lat, lon = float(lat), float(lon)
    except (ValueError, TypeError):
        lat, lon = default_lat, default_lon
        location_name = default_name
    
    # Check for cached weather data
    try:
        location = WeatherLocation.objects.get(latitude=lat, longitude=lon)
        cached_current = location.weather_data.filter(
            timestamp__gte=timezone.now() - timedelta(minutes=30),
            timestamp__lte=timezone.now()
        ).first()
        
        if cached_current and cached_current.is_current:
            # Use cached data
            forecast = location.weather_data.filter(
                timestamp__gt=timezone.now()
            ).order_by('timestamp')[:8]
            
            weather_data = {
                'current': cached_current,
                'forecast': list(forecast),
                'location': location
            }
            error = None
        else:
            # Fetch fresh data
            weather_data, error = fetch_weather_data(lat, lon, location_name)
    except WeatherLocation.DoesNotExist:
        # Fetch fresh data
        weather_data, error = fetch_weather_data(lat, lon, location_name)
    
    if error:
        messages.error(request, error)
        weather_data = None
    
    # Get recent locations for quick access
    recent_locations = WeatherLocation.objects.all().order_by('-created_at')[:5]
    
    # Get all countries for the location dropdown
    countries = Country.objects.all().order_by('name')
    
    context = {
        'weather_data': weather_data,
        'recent_locations': recent_locations,
        'api_configured': get_openweather_api_key() is not None,
        'countries': countries,
    }
    
    return render(request, 'weather/dashboard.html', context)


def weather_search_view(request):
    """
    Search for weather by hierarchical location and city name.
    
    Handles POST requests to search for locations using OpenWeatherMap geocoding API.
    Supports hierarchical location selection (country + region + city) for better accuracy.
    Prioritizes results from Kyrgyzstan and Central Asian countries.
    
    POST parameters:
        country: Country ID for hierarchical search
        region: Region ID for hierarchical search (optional)
        city_name: City name to search for
        city_text: Alternative text-based city search (fallback)
    
    Returns:
        If single result: Redirects to weather dashboard with coordinates
        If multiple results: Shows location selection page for disambiguation
        If no results: Redirects to dashboard with error message
    """
    if request.method == 'POST':
        # Get form data
        country_id = request.POST.get('country')
        region_id = request.POST.get('region')
        city_name = request.POST.get('city_name', '').strip()
        
        # Check if we have the minimum required data
        if city_name and country_id:
            try:
                # Get country and region information
                country = Country.objects.get(id=country_id)
                region = None
                if region_id:
                    region = Region.objects.get(id=region_id)
                
                # Build search query for better accuracy
                search_query = city_name
                
                # Add region to search if available
                if region:
                    search_query = f"{city_name}, {region.name}"
                
                # Add country for better accuracy
                search_query = f"{search_query}, {country.name}"
                
                # Search using OpenWeatherMap geocoding
                api_key = get_openweather_api_key()
                if api_key:
                    try:
                        geo_url = "http://api.openweathermap.org/geo/1.0/direct"
                        params = {
                            'q': search_query,
                            'limit': 5,  # Get multiple results to find best match
                            'appid': api_key
                        }
                        response = requests.get(geo_url, params=params, timeout=10)
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data:
                                # Prioritize results from the selected country
                                country_matches = [loc for loc in data if loc.get('country') == country.code]
                                
                                if country_matches:
                                    location = country_matches[0]  # Take the first match from the country
                                else:
                                    location = data[0]  # Fallback to first result
                                
                                location_name = f"{city_name}, {country.name}"
                                return redirect(f"/weather/?lat={location['lat']}&lon={location['lon']}&location={location_name}")
                            else:
                                messages.error(request, f"Weather data not found for '{city_name}' in {country.name}")
                        else:
                            messages.error(request, "Failed to fetch weather data from API.")
                    except Exception as e:
                        messages.error(request, f"Weather search error: {str(e)}")
                else:
                    messages.error(request, "Weather API not configured.")
                    
            except Country.DoesNotExist:
                messages.error(request, "Selected country not found.")
            except Region.DoesNotExist:
                messages.error(request, "Selected region not found.")
        
        # Fallback to old text-based search for backward compatibility
        elif request.POST.get('city_text'):
            city_name = request.POST.get('city_text', '').strip()
        
        if city_name and not country_id:
            # Use OpenWeatherMap geocoding API
            api_key = get_openweather_api_key()
            if api_key:
                try:
                    geo_url = "http://api.openweathermap.org/geo/1.0/direct"
                    
                    # Clean up the search term
                    search_term = city_name.title()  # Capitalize properly
                    
                    params = {
                        'q': search_term,
                        'limit': 10,  # Get up to 10 results for better disambiguation
                        'appid': api_key
                    }
                    response = requests.get(geo_url, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if data:
                            # Sort results to prioritize Kyrgyzstan (KG) and nearby countries
                            priority_countries = ['KG', 'KZ', 'TJ', 'UZ']  # Central Asian countries
                            data = sorted(data, key=lambda x: (
                                0 if x.get('country') == 'KG' else
                                1 if x.get('country') in priority_countries else
                                2
                            ))
                            
                            # Add country names for better display
                            country_names = {
                                'KG': 'Kyrgyzstan', 'KZ': 'Kazakhstan', 'TJ': 'Tajikistan', 'UZ': 'Uzbekistan',
                                'US': 'United States', 'GB': 'United Kingdom', 'FR': 'France', 'DE': 'Germany',
                                'CN': 'China', 'RU': 'Russia', 'IN': 'India', 'JP': 'Japan', 'CA': 'Canada',
                                'AU': 'Australia', 'BR': 'Brazil', 'MX': 'Mexico', 'AR': 'Argentina', 'IT': 'Italy',
                                'ES': 'Spain', 'TR': 'Turkey', 'EG': 'Egypt', 'ZA': 'South Africa', 'NG': 'Nigeria'
                            }
                            
                            for location in data:
                                country_code = location.get('country', '')
                                location['country_name'] = country_names.get(country_code, country_code)
                            
                            # If only one result, redirect directly
                            if len(data) == 1:
                                location = data[0]
                                return redirect(f"/weather/?lat={location['lat']}&lon={location['lon']}&location={location['name']}")
                            else:
                                # Multiple results - show selection page
                                return render(request, 'weather/location_selection.html', {
                                    'locations': data,
                                    'search_term': city_name
                                })
                        else:
                            messages.error(request, f"Location '{city_name}' not found.")
                    else:
                        messages.error(request, "Failed to search location.")
                except Exception as e:
                    messages.error(request, f"Search error: {str(e)}")
            else:
                messages.error(request, "Weather API not configured.")
        else:
            messages.error(request, "Please enter a city name.")
    
    return redirect('weather:dashboard')