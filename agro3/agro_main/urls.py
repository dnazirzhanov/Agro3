"""
URL configuration for agro_main project.

This module defines the main URL routing for the Agro3 agricultural application,
including all app-specific URL patterns and the home page view.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
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


from locations.views import LocationSearchPageView

# Language-independent URLs (API endpoints, media files, etc.)
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # Language switcher
    path('api/users/', include('users.api_urls')),
]

# Language-dependent URLs (all user-facing pages)
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('search/', LocationSearchPageView.as_view(), name='location_search'),
    path('locations/', include('locations.urls')),
    path('users/', include('users.urls')),
    path('crops/', include('crops.urls')),
    path('pests-diseases/', include('pests_diseases.urls')),
    path('market/', include('market.urls')),
    path('soil/', include('soil.urls')),
    path('forum/', include('forum.urls')),
    path('weather/', include('weather.urls')),
    path('agro-supplies/', include('agro_supplies.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    prefix_default_language=True,  # Include language prefix for default language too
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
