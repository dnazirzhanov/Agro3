#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agro_main.settings')
django.setup()

from agro_supplies.models import Shop
from locations.models import Country, Region, City

def create_sample_shop():
    # Get or create location data
    country, _ = Country.objects.get_or_create(
        name='Kyrgyzstan',
        defaults={'code': 'KG'}
    )
    
    region, _ = Region.objects.get_or_create(
        name='Batken Region',
        country=country,
        defaults={'code': 'BT'}
    )
    
    city, _ = City.objects.get_or_create(
        name='Batken',
        region=region,
        defaults={'country': country}
    )
    
    # Create or update sample shop with new contact fields
    shop, created = Shop.objects.get_or_create(
        name='AgroMart Batken',
        defaults={
            'shop_type': 'retail',
            'owner_name': 'Amantur Isaev',
            'phone_number': '+996555123456',
            'whatsapp_number': '+996777123456',
            'email': 'info@agromart-batken.kg',
            'website': 'https://agromart-batken.kg',
            'google_maps_link': 'https://maps.google.com/?q=40.0628,70.8172',
            'country': country,
            'region': region,
            'city': city,
            'address': 'Lenin Street 45, Near Central Bazaar, Batken 722800',
            'license_number': 'LIC-2023-BT-001',
            'established_year': 2018,
            'description': 'Leading agricultural supplies store in Batken region. We specialize in fertilizers, pesticides, and farming equipment. Serving farmers for over 5 years with quality products and expert advice.',
            'working_hours': 'Mon-Sat: 8:00 AM - 6:00 PM, Sun: 9:00 AM - 4:00 PM',
            'delivery_available': True,
            'delivery_radius_km': 50,
            'is_active': True,
            'is_verified': True,
        }
    )
    
    if created:
        print(f"✅ Created sample shop: {shop.name}")
    else:
        print(f"✅ Shop already exists: {shop.name}")
        # Update with new fields if they don't exist
        if not shop.whatsapp_number:
            shop.whatsapp_number = '+996777123456'
        if not shop.google_maps_link:
            shop.google_maps_link = 'https://maps.google.com/?q=40.0628,70.8172'
        shop.save()
        print(f"✅ Updated shop with new contact fields")
    
    print(f"📍 Shop Location: {shop.get_location_display()}")
    print(f"📞 Phone: {shop.phone_number}")
    print(f"💬 WhatsApp: {shop.whatsapp_number}")
    print(f"🗺️  Maps: {shop.google_maps_link}")
    print(f"🔗 Shop URL: /en/agro-supplies/shops/{shop.pk}/")
    
    return shop

if __name__ == '__main__':
    create_sample_shop()