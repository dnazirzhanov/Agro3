from django.db import models
from django.utils import timezone
from datetime import timedelta


class WeatherLocation(models.Model):
    """Store weather locations for caching and user preferences."""
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    country = models.CharField(max_length=2, help_text='Country code')
    state = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['latitude', 'longitude']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name}, {self.country}"


class WeatherData(models.Model):
    """Cache weather data to reduce API calls."""
    location = models.ForeignKey(WeatherLocation, on_delete=models.CASCADE, related_name='weather_data')
    timestamp = models.DateTimeField()
    temperature = models.FloatField(help_text='Temperature in Celsius')
    feels_like = models.FloatField(help_text='Feels like temperature in Celsius')
    humidity = models.PositiveIntegerField(help_text='Humidity percentage')
    pressure = models.FloatField(help_text='Atmospheric pressure in hPa')
    wind_speed = models.FloatField(help_text='Wind speed in m/s')
    wind_direction = models.PositiveIntegerField(help_text='Wind direction in degrees')
    weather_main = models.CharField(max_length=50, help_text='Main weather condition')
    weather_description = models.CharField(max_length=100, help_text='Weather description')
    weather_icon = models.CharField(max_length=10, help_text='Weather icon code')
    visibility = models.PositiveIntegerField(null=True, blank=True, help_text='Visibility in meters')
    uv_index = models.FloatField(null=True, blank=True, help_text='UV index')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
        unique_together = ['location', 'timestamp']
    
    def __str__(self):
        return f"{self.location.name} - {self.timestamp.strftime('%Y-%m-%d %H:%M')} - {self.temperature}°C"
    
    @property
    def is_current(self):
        """Check if weather data is recent (less than 30 minutes old)."""
        return timezone.now() - self.created_at < timedelta(minutes=30)
    
    @property
    def wind_direction_text(self):
        """Convert wind direction degrees to text."""
        directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                     'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        index = round(self.wind_direction / 22.5) % 16
        return directions[index]