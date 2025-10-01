from django.core.management.base import BaseCommand
from locations.models import Country, Region, City


class Command(BaseCommand):
    help = 'Populate initial location data for Kyrgyzstan and USA'
    
    def handle(self, *args, **options):
        # Create Kyrgyzstan
        kyrgyzstan, created = Country.objects.get_or_create(
            code='KG',
            defaults={'name': 'Kyrgyzstan'}
        )
        
        if created:
            self.stdout.write(f"Created country: {kyrgyzstan.name}")
        
        # Kyrgyzstan oblasts
        kg_regions = [
            ('Batken Oblast', 'Oblast'),
            ('Chuy Oblast', 'Oblast'),
            ('Issyk-Kul Oblast', 'Oblast'),
            ('Jalal-Abad Oblast', 'Oblast'),
            ('Naryn Oblast', 'Oblast'),
            ('Osh Oblast', 'Oblast'),
            ('Talas Oblast', 'Oblast'),
        ]
        
        for region_name, type_name in kg_regions:
            region, created = Region.objects.get_or_create(
                country=kyrgyzstan,
                name=region_name,
                defaults={'type_name': type_name}
            )
            if created:
                self.stdout.write(f"Created region: {region.name}")
        
        # Create some cities for Batken Oblast (since that's the original region)
        batken_oblast = Region.objects.get(country=kyrgyzstan, name='Batken Oblast')
        batken_cities = [
            ('Batken', 'city'),
            ('Kyzyl-Kiya', 'city'),
            ('Sulukta', 'town'),
            ('Kadamjay', 'town'),
            ('Leylek', 'village'),
        ]
        
        for city_name, type_name in batken_cities:
            city, created = City.objects.get_or_create(
                region=batken_oblast,
                name=city_name,
                defaults={'type_name': type_name}
            )
            if created:
                self.stdout.write(f"Created city: {city.name}")
        
        # Create USA
        usa, created = Country.objects.get_or_create(
            code='US',
            defaults={'name': 'United States'}
        )
        
        if created:
            self.stdout.write(f"Created country: {usa.name}")
        
        # Some US states
        us_states = [
            'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California',
            'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia',
            'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa',
            'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland',
            'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri',
            'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey',
            'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio',
            'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina',
            'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont',
            'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'
        ]
        
        for state_name in us_states:
            state, created = Region.objects.get_or_create(
                country=usa,
                name=state_name,
                defaults={'type_name': 'State'}
            )
            if created:
                self.stdout.write(f"Created state: {state.name}")
        
        # Add some Russian regions as well
        russia, created = Country.objects.get_or_create(
            code='RU',
            defaults={'name': 'Russia'}
        )
        
        if created:
            self.stdout.write(f"Created country: {russia.name}")
        
        # Some Russian oblasts
        russian_regions = [
            ('Moscow Oblast', 'Oblast'),
            ('Saint Petersburg', 'Federal City'),
            ('Leningrad Oblast', 'Oblast'),
            ('Novosibirsk Oblast', 'Oblast'),
            ('Sverdlovsk Oblast', 'Oblast'),
            ('Nizhny Novgorod Oblast', 'Oblast'),
            ('Tatarstan Republic', 'Republic'),
            ('Chelyabinsk Oblast', 'Oblast'),
            ('Omsk Oblast', 'Oblast'),
            ('Samara Oblast', 'Oblast'),
        ]
        
        for region_name, type_name in russian_regions:
            region, created = Region.objects.get_or_create(
                country=russia,
                name=region_name,
                defaults={'type_name': type_name}
            )
            if created:
                self.stdout.write(f"Created region: {region.name}")
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated location data!')
        )