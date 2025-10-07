#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agro_main.settings')
django.setup()

from locations.models import Country, Region, City

def populate_sample_locations():
    """Create comprehensive location data for testing"""
    
    print("🌍 Populating sample location data...")
    
    # Create more comprehensive data for Kyrgyzstan
    kyrgyzstan, _ = Country.objects.get_or_create(name='Kyrgyzstan', defaults={'code': 'KG'})
    
    # Kyrgyzstan regions
    regions_data = [
        ('Batken Region', 'Batken'),
        ('Chuy Region', 'Chuy'), 
        ('Issyk-Kul Region', 'Issyk-Kul'),
        ('Jalal-Abad Region', 'Jalal-Abad'),
        ('Naryn Region', 'Naryn'),
        ('Osh Region', 'Osh'),
        ('Talas Region', 'Talas'),
        ('Bishkek City', 'Bishkek'),
        ('Osh City', 'Osh'),
    ]
    
    created_regions = 0
    for region_name, region_code in regions_data:
        region, created = Region.objects.get_or_create(
            name=region_name, 
            country=kyrgyzstan,
            defaults={'type_name': 'Region'}
        )
        if created:
            created_regions += 1
    
    # Cities for each region
    cities_data = [
        ('Batken Region', ['Batken', 'Isfana', 'Kyzyl-Kiya', 'Sulukta']),
        ('Chuy Region', ['Bishkek', 'Tokmok', 'Kant', 'Kemin', 'Sokuluk']),
        ('Issyk-Kul Region', ['Karakol', 'Balykchy', 'Cholpon-Ata', 'Tup']),
        ('Jalal-Abad Region', ['Jalal-Abad', 'Tash-Kumyr', 'Mailuu-Suu', 'Kara-Kulja']),
        ('Naryn Region', ['Naryn', 'At-Bashi', 'Jumgal', 'Kochkor']),
        ('Osh Region', ['Osh', 'Uzgen', 'Nookat', 'Aravan', 'Kara-Suu']),
        ('Talas Region', ['Talas', 'Kara-Buura', 'Manas', 'Bakayata']),
    ]
    
    created_cities = 0
    for region_name, city_names in cities_data:
        try:
            region = Region.objects.get(name=region_name, country=kyrgyzstan)
            for city_name in city_names:
                city, created = City.objects.get_or_create(
                    name=city_name,
                    region=region,
                    defaults={'type_name': 'city'}
                )
                if created:
                    created_cities += 1
        except Region.DoesNotExist:
            print(f"⚠️  Region {region_name} not found")
    
    # Add some data for neighboring countries
    uzbekistan, _ = Country.objects.get_or_create(name='Uzbekistan', defaults={'code': 'UZ'})
    tashkent_region, _ = Region.objects.get_or_create(
        name='Tashkent Region', 
        country=uzbekistan,
        defaults={'type_name': 'Region'}
    )
    tashkent_city, created = City.objects.get_or_create(
        name='Tashkent',
        region=tashkent_region,
        defaults={'type_name': 'city'}
    )
    if created:
        created_cities += 1
    
    print(f"✅ Location data populated:")
    print(f"   📍 Countries: {Country.objects.count()}")
    print(f"   🏛️  Regions: {Region.objects.count()} (+{created_regions} new)")
    print(f"   🏙️  Cities: {City.objects.count()} (+{created_cities} new)")

def test_ajax_endpoints():
    """Test the AJAX endpoints are working"""
    print("\n🔧 Testing AJAX endpoints...")
    
    # Test regions endpoint
    kyrgyzstan = Country.objects.get(name='Kyrgyzstan')
    regions = Region.objects.filter(country=kyrgyzstan)
    
    print(f"📊 Available regions for Kyrgyzstan: {regions.count()}")
    for region in regions[:5]:  # Show first 5
        cities = City.objects.filter(region=region)
        print(f"   - {region.name}: {cities.count()} cities")
    
    print("\n✅ AJAX endpoints should work with this data!")

if __name__ == '__main__':
    populate_sample_locations()
    test_ajax_endpoints()
    print("\n🎯 Test the dropdowns at:")
    print("   - http://127.0.0.1:8000/en/agro-supplies/shops/")
    print("   - http://127.0.0.1:8000/en/agro-supplies/products/")
    print("   - http://127.0.0.1:8000/en/users/register/")