"""
Management command to populate sample multilingual market data.
This creates test data with proper translations in English, Russian, and Kyrgyz.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from market.models import Product, Market, MarketPrice
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Populate sample multilingual market data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing market data before adding new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('🗑️  Clearing existing market data...')
            MarketPrice.objects.all().delete()
            Product.objects.all().delete()
            Market.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✅ Existing data cleared'))

        self.stdout.write('🌱 Creating sample multilingual market data...')
        
        # Sample products with translations
        products_data = [
            {
                'name_en': 'Wheat', 'name_ru': 'Пшеница', 'name_ky': 'Буудай',
                'category_en': 'Grains', 'category_ru': 'Зерновые', 'category_ky': 'Дан дыйлалар',
                'description_en': 'High quality wheat grain', 'description_ru': 'Высококачественная пшеница', 'description_ky': 'Жогорку сапаттуу буудай'
            },
            {
                'name_en': 'Apples', 'name_ru': 'Яблоки', 'name_ky': 'Алмалар',
                'category_en': 'Fruits', 'category_ru': 'Фрукты', 'category_ky': 'Жемиштер',
                'description_en': 'Fresh red apples', 'description_ru': 'Свежие красные яблоки', 'description_ky': 'Жаңы кызыл алмалар'
            },
            {
                'name_en': 'Potatoes', 'name_ru': 'Картофель', 'name_ky': 'Картошка',
                'category_en': 'Vegetables', 'category_ru': 'Овощи', 'category_ky': 'Жашылчалар',
                'description_en': 'Local grown potatoes', 'description_ru': 'Местный картофель', 'description_ky': 'Жергиликтүү картошка'
            },
            {
                'name_en': 'Onions', 'name_ru': 'Лук', 'name_ky': 'Пияз',
                'category_en': 'Vegetables', 'category_ru': 'Овощи', 'category_ky': 'Жашылчалар',
                'description_en': 'Yellow onions', 'description_ru': 'Желтый лук', 'description_ky': 'Сары пияз'
            },
            {
                'name_en': 'Tomatoes', 'name_ru': 'Помидоры', 'name_ky': 'Помидор',
                'category_en': 'Vegetables', 'category_ru': 'Овощи', 'category_ky': 'Жашылчалар',
                'description_en': 'Fresh red tomatoes', 'description_ru': 'Свежие красные помидоры', 'description_ky': 'Жаңы кызыл помидор'
            },
        ]

        # Sample markets with translations
        markets_data = [
            {
                'name_en': 'Batken Central Market', 'name_ru': 'Баткенский центральный рынок', 'name_ky': 'Баткен борбордук базары',
                'location': 'Batken City Center',
                'description_en': 'Main agricultural market in Batken region', 'description_ru': 'Главный сельскохозяйственный рынок Баткенской области', 'description_ky': 'Баткен облусундагы негизги айыл чарба базары',
                'contact_info': '+996 555 123 456'
            },
            {
                'name_en': 'Isfana Farmers Market', 'name_ru': 'Исфанинский фермерский рынок', 'name_ky': 'Исфана фермер базары',
                'location': 'Isfana District',
                'description_en': 'Local farmers market with fresh produce', 'description_ru': 'Местный фермерский рынок со свежими продуктами', 'description_ky': 'Жаңы өнүмдөр менен жергиликтүү фермер базары',
                'contact_info': '+996 555 234 567'
            },
            {
                'name_en': 'Kadamjay Agricultural Market', 'name_ru': 'Кадамжайский сельскохозяйственный рынок', 'name_ky': 'Кадамжай айыл чарба базары',
                'location': 'Kadamjay Town',
                'description_en': 'Agricultural products and livestock market', 'description_ru': 'Рынок сельскохозяйственной продукции и скота', 'description_ky': 'Айыл чарба продукттары жана мал базары',
                'contact_info': '+996 555 345 678'
            },
        ]

        # Create products
        products = []
        for data in products_data:
            product = Product.objects.create(**data)
            products.append(product)
            self.stdout.write(f'  ✅ Created product: {product.name}')

        # Create markets
        markets = []
        for data in markets_data:
            market = Market.objects.create(**data)
            markets.append(market)
            self.stdout.write(f'  ✅ Created market: {market.name}')

        # Create sample prices with multilingual notes
        price_notes_samples = [
            {
                'notes_en': 'Excellent quality, freshly harvested',
                'notes_ru': 'Отличное качество, свежесобранное',
                'notes_ky': 'Эң жакшы сапат, жаңы жыйналган'
            },
            {
                'notes_en': 'Organic produce, no pesticides used',
                'notes_ru': 'Органические продукты, без пестицидов',
                'notes_ky': 'Органикалык продукт, пестицид жок'
            },
            {
                'notes_en': 'Limited quantity available',
                'notes_ru': 'Ограниченное количество',
                'notes_ky': 'Чектелген сан'
            },
            {
                'notes_en': 'Best price in the region',
                'notes_ru': 'Лучшая цена в регионе',
                'notes_ky': 'Аймактагы эң жакшы баа'
            },
            {
                'notes_en': 'Direct from local farms',
                'notes_ru': 'Прямо с местных ферм',
                'notes_ky': 'Жергиликтүү фермалардан түз'
            },
        ]

        # Create price entries for the last 30 days
        prices_created = 0
        for i in range(30):
            date = timezone.now() - timedelta(days=i)
            
            # Create 2-5 random price entries per day
            for _ in range(random.randint(2, 5)):
                product = random.choice(products)
                market = random.choice(markets)
                
                # Base prices for different products (in som)
                base_prices = {
                    'Wheat': 35.0, 'Apples': 80.0, 'Potatoes': 25.0, 
                    'Onions': 30.0, 'Tomatoes': 45.0
                }
                
                # Add some price variation (+/- 20%)
                base_price = base_prices.get(product.name_en, 50.0)
                price = base_price * (0.8 + random.random() * 0.4)
                
                # Random unit
                units = ['kg', 'piece', 'bundle', 'liter', 'box']
                unit = random.choice(units)
                
                # Random notes
                notes_data = random.choice(price_notes_samples) if random.random() > 0.3 else {}
                
                # Check if price already exists for this product, market, and date
                if not MarketPrice.objects.filter(
                    product=product, 
                    market=market, 
                    date_recorded__date=date.date()
                ).exists():
                    MarketPrice.objects.create(
                        product=product,
                        market=market,
                        price=round(price, 2),
                        unit=unit,
                        date_recorded=date,
                        **notes_data
                    )
                    prices_created += 1

        self.stdout.write(f'  ✅ Created {prices_created} price entries')

        self.stdout.write(self.style.SUCCESS('\n🎉 Sample multilingual market data created successfully!'))
        self.stdout.write(self.style.SUCCESS(f'📊 Summary:'))
        self.stdout.write(f'   - Products: {len(products)}')
        self.stdout.write(f'   - Markets: {len(markets)}') 
        self.stdout.write(f'   - Price entries: {prices_created}')
        self.stdout.write(self.style.SUCCESS('\n💡 You can now test the multilingual market system:'))
        self.stdout.write('   - English: /en/market/')
        self.stdout.write('   - Russian: /ru/market/')
        self.stdout.write('   - Kyrgyz: /ky/market/')