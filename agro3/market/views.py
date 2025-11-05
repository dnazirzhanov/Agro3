"""
Views for market price tracking and comparison.

This module handles HTTP requests for displaying market prices, filtering prices
by product and market, comparing prices across markets, and providing price
statistics to help farmers make informed selling decisions.
"""
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Avg, Max, Min, Q
from django.utils.translation import gettext_lazy as _, get_language
from .models import MarketPrice, Product, Market
from datetime import datetime, timedelta
from django.utils import timezone


def filter_by_language(queryset, model_class, language_code):
    """
    Filter queryset to only include objects that have translations in the specified language.
    
    For Products: Only show products with name in the user's language
    For Markets: Only show markets with name in the user's language
    """
    if language_code == 'en':
        # English is the default language, always show all objects
        return queryset
    
    # For non-English languages, filter objects that have translation
    if model_class == Product:
        # Filter products that have name in the specified language
        field_name = f'name_{language_code}'
        return queryset.filter(**{f'{field_name}__isnull': False}).exclude(**{field_name: ''})
    elif model_class == Market:
        # Filter markets that have name in the specified language
        field_name = f'name_{language_code}'
        return queryset.filter(**{f'{field_name}__isnull': False}).exclude(**{field_name: ''})
    
    return queryset


def market_price_list_view(request):
    """
    Display market prices with filtering and search.
    
    Only shows products and markets that have translations in the user's chosen language.
    This ensures users only see content they can understand.
    
    Handles GET requests with optional filters:
    - product: Filter by product ID
    - market: Filter by market ID
    - date_range: Filter by days (1, 7, 30, 90)
    - search: Search products by name
    - page: Pagination (20 prices per page)
    
    Returns:
        Paginated list of market prices with optional price statistics
        for the selected product including average, minimum, and maximum prices
    """
    current_language = get_language()
    
    # Get all products and markets with translations in user's language
    available_products = filter_by_language(Product.objects.all(), Product, current_language)
    available_markets = filter_by_language(Market.objects.all(), Market, current_language)
    
    # Only show prices for products and markets that have translations in user's language
    prices = MarketPrice.objects.select_related('product', 'market').filter(
        product__in=available_products,
        market__in=available_markets
    )
    
    # Filter by product
    product_filter = request.GET.get('product')
    if product_filter:
        # Ensure the selected product has translation in user's language
        try:
            selected_product = available_products.get(id=product_filter)
            prices = prices.filter(product=selected_product)
        except Product.DoesNotExist:
            # Product doesn't have translation in user's language, reset filter
            product_filter = None
    
    # Filter by market
    market_filter = request.GET.get('market')
    if market_filter:
        # Ensure the selected market has translation in user's language
        try:
            selected_market = available_markets.get(id=market_filter)
            prices = prices.filter(market=selected_market)
        except Market.DoesNotExist:
            # Market doesn't have translation in user's language, reset filter
            market_filter = None
    
    # Filter by date range
    date_filter = request.GET.get('date_range', '7')  # Default to last 7 days
    if date_filter:
        try:
            days = int(date_filter)
            start_date = timezone.now() - timedelta(days=days)
            prices = prices.filter(date_recorded__gte=start_date)
        except ValueError:
            pass
    
    # Search by product name (search in user's language)
    search = request.GET.get('search')
    if search:
        if current_language == 'en':
            prices = prices.filter(product__name__icontains=search)
        else:
            # Search in translated field
            search_field = f'product__name_{current_language}__icontains'
            prices = prices.filter(**{search_field: search})
    
    # Pagination
    paginator = Paginator(prices, 20)
    page_number = request.GET.get('page')
    prices = paginator.get_page(page_number)
    
    # Price statistics
    stats = None
    if product_filter:
        try:
            product = available_products.get(pk=product_filter)
            recent_prices = MarketPrice.objects.filter(
                product=product,
                date_recorded__gte=timezone.now() - timedelta(days=30)
            )
            if recent_prices.exists():
                stats = {
                    'product': product,
                    'avg_price': recent_prices.aggregate(Avg('price'))['price__avg'],
                    'min_price': recent_prices.aggregate(Min('price'))['price__min'],
                    'max_price': recent_prices.aggregate(Max('price'))['price__max'],
                    'count': recent_prices.count(),
                }
        except Product.DoesNotExist:
            pass
    
    context = {
        'prices': prices,
        'products': available_products,
        'markets': available_markets,
        'current_product': product_filter,
        'current_market': market_filter,
        'current_date_range': date_filter,
        'current_search': search or '',
        'stats': stats,
        'current_language': current_language,
        'date_range_choices': [
            ('1', _('Today')),
            ('7', _('Last 7 days')),
            ('30', _('Last 30 days')),
            ('90', _('Last 3 months')),
        ],
    }
    
    return render(request, 'market/price_list.html', context)


def price_comparison_view(request):
    """
    Compare prices across different markets for the same product.
    
    Only shows products and markets that have translations in the user's chosen language.
    
    Handles GET requests to display price comparisons:
    - product: Product ID to compare prices for
    
    Returns:
        Price comparison page showing the latest prices (within last 7 days)
        for the selected product across all markets, enabling farmers to
        identify the best market for selling their produce
    """
    current_language = get_language()
    
    # Get products with translations in user's language
    available_products = filter_by_language(Product.objects.all(), Product, current_language)
    available_markets = filter_by_language(Market.objects.all(), Market, current_language)
    
    selected_product = None
    price_data = []
    
    product_id = request.GET.get('product')
    if product_id:
        try:
            selected_product = available_products.get(pk=product_id)
            
            # Get recent prices for this product across markets with translations in user's language
            recent_prices = MarketPrice.objects.filter(
                product=selected_product,
                market__in=available_markets,
                date_recorded__gte=timezone.now() - timedelta(days=7)
            ).select_related('market').order_by('market__name', '-date_recorded')
            
            # Group by market and get latest price
            market_prices = {}
            for price in recent_prices:
                if price.market.id not in market_prices:
                    market_prices[price.market.id] = price
            
            price_data = list(market_prices.values())
        except Product.DoesNotExist:
            # Product doesn't have translation in user's language
            pass
    
    context = {
        'products': available_products,
        'selected_product': selected_product,
        'price_data': price_data,
        'current_language': current_language,
    }
    
    return render(request, 'market/price_comparison.html', context)


def market_detail_view(request, pk):
    """
    Display all products and prices from a specific market/shop.
    
    Only shows the market if it has translation in user's language,
    and only shows products that have translations in user's language.
    """
    current_language = get_language()
    
    # Get markets with translations in user's language
    available_markets = filter_by_language(Market.objects.all(), Market, current_language)
    
    try:
        market = available_markets.get(pk=pk)
    except Market.DoesNotExist:
        # Market doesn't have translation in user's language, show 404
        raise get_object_or_404(Market, pk=pk)
    
    # Get products with translations in user's language
    available_products = filter_by_language(Product.objects.all(), Product, current_language)
    
    # Get all prices for this market, only for products with translations in user's language
    prices = MarketPrice.objects.filter(
        market=market,
        product__in=available_products
    ).select_related('product').order_by('product__name', '-date_recorded')
    
    # Group by product to get latest price for each product
    product_prices = {}
    for price in prices:
        if price.product.id not in product_prices:
            product_prices[price.product.id] = price
    
    latest_prices = list(product_prices.values())
    
    # Pagination
    paginator = Paginator(latest_prices, 20)
    page_number = request.GET.get('page')
    paginated_prices = paginator.get_page(page_number)
    
    context = {
        'market': market,
        'prices': paginated_prices,
        'current_language': current_language,
    }
    
    return render(request, 'market/market_detail.html', context)
