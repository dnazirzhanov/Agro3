"""
URL configuration for agro_main project.

This module defines the main URL routing for the Agro3 agricultural application,
including all app-specific URL patterns and the home page view.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render


def home_view(request):
    """
    Display the home page.
    
    Handles GET requests to render the main landing page of the agricultural
    application with links to all major features.
    
    Returns:
        Rendered home page template
    """
    return render(request, 'home.html')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('users/', include('users.urls')),
    path('crops/', include('crops.urls')),
    path('pests-diseases/', include('pests_diseases.urls')),
    path('market/', include('market.urls')),
    path('soil/', include('soil.urls')),
    path('forum/', include('forum.urls')),
    path('weather/', include('weather.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
