#!/usr/bin/env python

import os
import sys
import django

# Set up Django
sys.path.append('/workspaces/Agro3/agro3')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agro_main.settings')
django.setup()

from weather.views import weather_search_view
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage

# Create a test request
factory = RequestFactory()

# Test Uch-Korgon (should show 2 results)
print("Testing 'Uch-Korgon' search:")
request = factory.post('/weather/search/', {'city': 'Uch-Korgon'})
request.session = {}
request._messages = FallbackStorage(request)

try:
    response = weather_search_view(request)
    print(f"Response status: {response.status_code}")
    if hasattr(response, 'context_data'):
        locations = response.context_data.get('locations', [])
        print(f"Found {len(locations)} locations:")
        for i, loc in enumerate(locations):
            print(f"  {i+1}. {loc['name']}, {loc.get('state', 'N/A')}, {loc['country']}")
    elif hasattr(response, 'url'):
        print(f"Redirect to: {response.url}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*50 + "\n")

# Test Springfield (should show 5 results)
print("Testing 'Springfield' search:")
request = factory.post('/weather/search/', {'city': 'Springfield'})
request.session = {}
request._messages = FallbackStorage(request)

try:
    response = weather_search_view(request)
    print(f"Response status: {response.status_code}")
    if hasattr(response, 'context_data'):
        locations = response.context_data.get('locations', [])
        print(f"Found {len(locations)} locations:")
        for i, loc in enumerate(locations):
            print(f"  {i+1}. {loc['name']}, {loc.get('state', 'N/A')}, {loc['country']}")
    elif hasattr(response, 'url'):
        print(f"Redirect to: {response.url}")
except Exception as e:
    print(f"Error: {e}")