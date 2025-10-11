"""
Management command to populate market data with multilingual support demonstration.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from market.models import Product, Market, MarketPrice
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Populate market data with sample prices for testing multilingual units'

    def handle(self, *args, **options):
        # Create some sample products if they don't exist
        products_data = [
            {'name': 'Tomatoes', 'category': 'Vegetables'},
            {'name': 'Potatoes', 'category': 'Vegetables'},
            {'name': 'Apples', 'category': 'Fruits'},
            {'name': 'Carrots', 'category': 'Vegetables'},
            {'name': 'Onions', 'category': 'Vegetables'},
        ]
        
        products = []
        for prod_data in products_data:
            product, created = Product.objects.get_or_create(
                name=prod_data['name'],
                defaults={'category': prod_data['category']}
            )
            products.append(product)
            if created:
                self.stdout.write(f"Created product: {product.name}")

        # Create some sample markets if they don't exist
        markets_data = [
            {'name': 'Central Market', 'location': 'Batken City Center'},
            {'name': 'Farmers Market', 'location': 'Kadamjay District'},
            {'name': 'Regional Market', 'location': 'Isfana Township'},
        ]
        
        markets = []
        for market_data in markets_data:
            market, created = Market.objects.get_or_create(
                name=market_data['name'],
                defaults={'location': market_data['location']}
            )
            markets.append(market)
            if created:
                self.stdout.write(f"Created market: {market.name}")

        # Create sample prices with different units
        units = ['kg', 'piece', 'bundle', 'liter', 'box']
        
        # Generate prices for the last 30 days
        for i in range(30):
            date = timezone.now() - timedelta(days=i)
            
            for product in products:
                for market in markets:
                    # Skip some combinations to make it more realistic
                    if random.random() < 0.3:  # 30% chance to skip
                        continue
                    
                    # Choose appropriate unit based on product
                    if product.name in ['Tomatoes', 'Potatoes', 'Carrots', 'Onions']:
                        unit = random.choice(['kg', 'box'])
                    elif product.name == 'Apples':
                        unit = random.choice(['kg', 'piece', 'box'])
                    else:
                        unit = random.choice(units)
                    
                    # Generate realistic prices based on unit
                    if unit == 'kg':
                        price = Decimal(str(random.uniform(30, 120)))
                    elif unit == 'piece':
                        price = Decimal(str(random.uniform(5, 25)))
                    elif unit == 'bundle':
                        price = Decimal(str(random.uniform(15, 40)))
                    elif unit == 'liter':
                        price = Decimal(str(random.uniform(40, 80)))
                    else:  # box
                        price = Decimal(str(random.uniform(200, 500)))
                    
                    # Check if this price already exists
                    existing = MarketPrice.objects.filter(
                        product=product,
                        market=market,
                        date_recorded__date=date.date()
                    ).first()
                    
                    if not existing:
                        MarketPrice.objects.create(
                            product=product,
                            market=market,
                            price=price.quantize(Decimal('0.01')),
                            unit=unit,
                            date_recorded=date
                        )
        
        total_prices = MarketPrice.objects.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated market data. Total prices: {total_prices}'
            )
        )