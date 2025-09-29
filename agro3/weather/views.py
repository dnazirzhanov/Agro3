import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta
from .models import WeatherLocation, WeatherData
import os


def get_openweather_api_key():
    """Get OpenWeatherMap API key from environment or settings."""
    return os.getenv('OPENWEATHER_API_KEY') or getattr(settings, 'OPENWEATHER_API_KEY', None)


def fetch_weather_data(lat, lon, location_name=None):
    """Fetch weather data from OpenWeatherMap API."""
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
    """Main weather dashboard with location search."""
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
    
    context = {
        'weather_data': weather_data,
        'recent_locations': recent_locations,
        'api_configured': get_openweather_api_key() is not None,
    }
    
    return render(request, 'weather/dashboard.html', context)


def weather_search_view(request):
    """Search for weather by city name."""
    if request.method == 'POST':
        city_name = request.POST.get('city', '').strip()
        if city_name:
            # Use OpenWeatherMap geocoding API
            api_key = get_openweather_api_key()
            if api_key:
                try:
                    geo_url = "http://api.openweathermap.org/geo/1.0/direct"
                    params = {
                        'q': city_name,
                        'limit': 5,  # Get up to 5 results for disambiguation
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