from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from locations.models import Country, Region, City
from agro_supplies.models import ChemicalCategory, ChemicalProduct, Shop, ChemicalPrice
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create sample chemical products and shops data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample agro supplies data...'))
        
        # Create categories
        categories_data = [
            ('fertilizer', 'NPK Fertilizers', 'Complete nutrient fertilizers with nitrogen, phosphorus, and potassium'),
            ('fertilizer', 'Organic Fertilizers', 'Natural organic fertilizers from plant and animal sources'),
            ('pesticide', 'Universal Pesticides', 'Broad-spectrum pest control products'),
            ('herbicide', 'Selective Herbicides', 'Targeted weed control for specific crops'),
            ('fungicide', 'Preventive Fungicides', 'Disease prevention and control products'),
            ('insecticide', 'Contact Insecticides', 'Fast-acting insect control products'),
        ]
        
        categories = {}
        for cat_type, name, desc in categories_data:
            category, created = ChemicalCategory.objects.get_or_create(
                name=name,
                category_type=cat_type,
                defaults={'description': desc}
            )
            categories[name] = category
            if created:
                self.stdout.write(f'Created category: {category}')
        
        # Create chemical products
        products_data = [
            # Fertilizers
            ('NPK 16-16-16', 'AgriCorp', categories['NPK Fertilizers'], '16% N, 16% P2O5, 16% K2O', 
             '16-16-16', 'Complete balanced fertilizer for all crops', 'Apply 200-300 kg per hectare', 
             '200-300 kg/ha', 'soil', 25, 'kg', 'Wheat, Corn, Barley, Vegetables', ''),
            
            ('NPK 20-10-10', 'FertilMax', categories['NPK Fertilizers'], '20% N, 10% P2O5, 10% K2O', 
             '20-10-10', 'High nitrogen fertilizer for leafy growth', 'Apply 150-250 kg per hectare', 
             '150-250 kg/ha', 'soil', 50, 'kg', 'Leafy vegetables, Corn', ''),
            
            ('Organic Compost', 'EcoFarm', categories['Organic Fertilizers'], 'Organic matter 65%', 
             'Organic', 'Premium organic fertilizer from composted materials', 'Apply 2-3 tons per hectare', 
             '2-3 tons/ha', 'soil', 20, 'kg', 'All crops, Vegetables, Fruits', ''),
            
            # Pesticides
            ('Cypermethrin 10% EC', 'CropGuard', categories['Universal Pesticides'], 'Cypermethrin 10%', 
             '10% EC', 'Broad spectrum insecticide for various pests', 'Mix 1-2ml per liter of water', 
             '1-2ml/L', 'spray', 1, 'liter', 'Cotton, Vegetables, Fruits', 'Aphids, Thrips, Bollworms'),
            
            ('Imidacloprid 17.8% SL', 'PestAway', categories['Universal Pesticides'], 'Imidacloprid 17.8%', 
             '17.8% SL', 'Systemic insecticide for sucking pests', 'Mix 0.5-1ml per liter of water', 
             '0.5-1ml/L', 'spray', 500, 'ml', 'Cotton, Rice, Vegetables', 'Aphids, Whiteflies, Thrips'),
            
            # Herbicides
            ('Glyphosate 41% SL', 'WeedKill', categories['Selective Herbicides'], 'Glyphosate 41%', 
             '41% SL', 'Non-selective herbicide for total weed control', 'Mix 3-5ml per liter of water', 
             '3-5ml/L', 'spray', 1, 'liter', 'All crops (pre-planting)', 'Annual and perennial weeds'),
            
            ('2,4-D Amine 58% SL', 'CropClean', categories['Selective Herbicides'], '2,4-D Amine 58%', 
             '58% SL', 'Selective herbicide for broadleaf weeds', 'Mix 2-3ml per liter of water', 
             '2-3ml/L', 'spray', 1, 'liter', 'Wheat, Rice, Corn', 'Broadleaf weeds'),
            
            # Fungicides
            ('Mancozeb 75% WP', 'FungiStop', categories['Preventive Fungicides'], 'Mancozeb 75%', 
             '75% WP', 'Protective fungicide for disease prevention', 'Mix 2-3g per liter of water', 
             '2-3g/L', 'spray', 1, 'kg', 'Tomatoes, Potatoes, Grapes', 'Late blight, Downy mildew'),
            
            ('Copper Oxychloride 50% WP', 'CopperShield', categories['Preventive Fungicides'], 'Copper Oxychloride 50%', 
             '50% WP', 'Copper-based fungicide for bacterial diseases', 'Mix 3-4g per liter of water', 
             '3-4g/L', 'spray', 1, 'kg', 'Citrus, Vegetables, Grapes', 'Bacterial spot, Canker'),
        ]
        
        created_products = []
        for product_data in products_data:
            product, created = ChemicalProduct.objects.get_or_create(
                name=product_data[0],
                brand=product_data[1],
                package_size=product_data[9],
                package_unit=product_data[10],
                defaults={
                    'category': product_data[2],
                    'active_ingredient': product_data[3],
                    'concentration': product_data[4],
                    'description': product_data[5],
                    'usage_instructions': product_data[6],
                    'dosage': product_data[7],
                    'application_method': product_data[8],
                    'target_crops': product_data[11],
                    'target_pests': product_data[12],
                    'safety_warnings': 'Follow label instructions. Use protective equipment.',
                }
            )
            created_products.append(product)
            if created:
                self.stdout.write(f'Created product: {product}')
        
        # Get or create countries and locations
        try:
            kyrgyzstan = Country.objects.get(name='Kyrgyzstan')
        except Country.DoesNotExist:
            kyrgyzstan = Country.objects.create(name='Kyrgyzstan', code='KG')
        
        try:
            russia = Country.objects.get(name='Russia')
        except Country.DoesNotExist:
            russia = Country.objects.create(name='Russia', code='RU')
        
        # Create regions for Kyrgyzstan
        regions_kg = ['Chuy', 'Issyk-Kul', 'Naryn', 'Talas', 'Osh', 'Jalal-Abad', 'Batken']
        kg_regions = []
        for region_name in regions_kg:
            region, created = Region.objects.get_or_create(
                name=region_name, 
                country=kyrgyzstan
            )
            kg_regions.append(region)
        
        # Create regions for Russia
        regions_ru = ['Moscow Oblast', 'Saint Petersburg', 'Krasnodar Krai', 'Rostov Oblast']
        ru_regions = []
        for region_name in regions_ru:
            region, created = Region.objects.get_or_create(
                name=region_name, 
                country=russia
            )
            ru_regions.append(region)
        
        # Create cities
        cities_data = [
            ('Bishkek', kg_regions[0]),
            ('Osh', kg_regions[4]),
            ('Jalal-Abad', kg_regions[5]),
            ('Moscow', ru_regions[0]),
            ('Krasnodar', ru_regions[2]),
        ]
        
        cities = []
        for city_name, region in cities_data:
            city, created = City.objects.get_or_create(
                name=city_name,
                region=region
            )
            cities.append(city)
        
        # Create shops
        shops_data = [
            ('Agro Center Bishkek', 'retail', 'Askar Toktomushev', '+996555123456', 'agro.bishkek@mail.kg', 
             cities[0], 'Chuy Avenue 125, Bishkek', 'Mon-Sat: 8AM-7PM'),
            
            ('Farm Supply Osh', 'wholesale', 'Bakyt Alimov', '+996777987654', 'farmsupply.osh@gmail.com', 
             cities[1], 'Lenin Street 45, Osh', 'Mon-Fri: 9AM-6PM, Sat: 9AM-2PM'),
            
            ('Agro Trade Jalal-Abad', 'distributor', 'Nurlan Isaev', '+996555456789', 'agrotrade.ja@mail.ru', 
             cities[2], 'Toktogul Street 78, Jalal-Abad', 'Mon-Sat: 8AM-6PM'),
            
            ('Moscow Agro Supply', 'wholesale', 'Ivan Petrov', '+7495123456', 'moscow.agro@yandex.ru', 
             cities[3], 'Agricultural Street 15, Moscow', 'Mon-Fri: 9AM-7PM'),
            
            ('Krasnodar Farm Center', 'retail', 'Sergey Volkov', '+7861234567', 'krasnodar.farm@mail.ru', 
             cities[4], 'Krasnaya Street 89, Krasnodar', 'Mon-Sat: 8AM-8PM'),
        ]
        
        created_shops = []
        for shop_data in shops_data:
            city = shop_data[5]
            shop, created = Shop.objects.get_or_create(
                name=shop_data[0],
                defaults={
                    'shop_type': shop_data[1],
                    'owner_name': shop_data[2],
                    'phone_number': shop_data[3],
                    'email': shop_data[4],
                    'country': city.region.country,
                    'region': city.region,
                    'city': city,
                    'address': shop_data[6],
                    'working_hours': shop_data[7],
                    'delivery_available': True,
                    'delivery_radius_km': 50,
                    'is_verified': True,
                }
            )
            created_shops.append(shop)
            if created:
                self.stdout.write(f'Created shop: {shop}')
        
        # Create prices for products in shops
        import random
        base_prices = {
            'fertilizer': (800, 1500),  # KGS per 25-50kg
            'pesticide': (1200, 2500),  # KGS per liter
            'herbicide': (1500, 3000),  # KGS per liter
            'fungicide': (900, 2000),   # KGS per kg
        }
        
        for product in created_products:
            # Each product available in 2-4 random shops
            available_shops = random.sample(created_shops, random.randint(2, 4))
            
            price_range = base_prices.get(product.category.category_type, (500, 2000))
            base_price = random.randint(price_range[0], price_range[1])
            
            for shop in available_shops:
                # Vary price by shop (±20%)
                variation = random.uniform(0.8, 1.2)
                shop_price = int(base_price * variation)
                
                price, created = ChemicalPrice.objects.get_or_create(
                    product=product,
                    shop=shop,
                    defaults={
                        'price': Decimal(str(shop_price)),
                        'currency': 'KGS',
                        'discount_percentage': random.choice([0, 5, 10, 15]),
                        'is_in_stock': random.choice([True, True, True, False]),  # 75% in stock
                        'stock_quantity': random.randint(5, 100),
                        'minimum_order': random.randint(1, 5),
                    }
                )
                if created:
                    self.stdout.write(f'Created price: {price}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created:\n'
                f'- {len(categories)} categories\n'
                f'- {len(created_products)} products\n'
                f'- {len(created_shops)} shops\n'
                f'- Price data for all products'
            )
        )