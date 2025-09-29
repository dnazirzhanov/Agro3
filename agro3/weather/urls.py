from django.urls import path
from . import views

app_name = 'weather'

urlpatterns = [
    path('', views.weather_dashboard_view, name='dashboard'),
    path('search/', views.weather_search_view, name='search'),
]