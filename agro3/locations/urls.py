from django.urls import path
from .views import GetRegionsView, GetCitiesView, SearchLocationsView, LocationSearchPageView

app_name = 'locations'

urlpatterns = [
    path('ajax/regions/', GetRegionsView.as_view(), name='get_regions'),
    path('ajax/cities/', GetCitiesView.as_view(), name='get_cities'),
    path('ajax/search/', SearchLocationsView.as_view(), name='search_locations'),
    path('search/', LocationSearchPageView.as_view(), name='location_search'),
]