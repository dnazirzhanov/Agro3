from django.test import TestCase
from django.utils import timezone
from .models import WeatherLocation, WeatherData


class WeatherModelsTest(TestCase):
    def setUp(self):
        self.location = WeatherLocation.objects.create(
            name='Batken',
            latitude=40.0628,
            longitude=70.8175,
            country='KG'
        )
    
    def test_weather_location_creation(self):
        self.assertEqual(str(self.location), 'Batken, KG')
        self.assertEqual(self.location.latitude, 40.0628)
    
    def test_weather_data_creation(self):
        weather = WeatherData.objects.create(
            location=self.location,
            timestamp=timezone.now(),
            temperature=25.5,
            feels_like=27.0,
            humidity=60,
            pressure=1013.25,
            wind_speed=3.5,
            wind_direction=180,
            weather_main='Clear',
            weather_description='clear sky',
            weather_icon='01d'
        )
        self.assertIn('Batken', str(weather))
        self.assertEqual(weather.wind_direction_text, 'S')