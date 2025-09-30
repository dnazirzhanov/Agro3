"""
Views for market price tracking and comparison.

This module handles HTTP requests for displaying market prices, filtering prices
by product and market, comparing prices across markets, and providing price
statistics to help farmers make informed selling decisions.
"""
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Avg, Max, Min
from .models import MarketPrice, Product, Market
from datetime import datetime, timedelta
from django.utils import timezone


def market_price_list_view(request):
    """
    Display market prices with filtering and search.
    
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
    prices = MarketPrice.objects.select_related('product', 'market')
    
    # Filter by product
    product_filter = request.GET.get('product')
    if product_filter:
        prices = prices.filter(product_id=product_filter)
    
    # Filter by market
    market_filter = request.GET.get('market')
    if market_filter:
        prices = prices.filter(market_id=market_filter)
    
    # Filter by date range
    date_filter = request.GET.get('date_range', '7')  # Default to last 7 days
    if date_filter:
        try:
            days = int(date_filter)
            start_date = timezone.now() - timedelta(days=days)
            prices = prices.filter(date_recorded__gte=start_date)
        except ValueError:
            pass
    
    # Search by product name
    search = request.GET.get('search')
    if search:
        prices = prices.filter(product__name__icontains=search)
    
    # Pagination
    paginator = Paginator(prices, 20)
    page_number = request.GET.get('page')
    prices = paginator.get_page(page_number)
    
    # Get filter options
    products = Product.objects.all()
    markets = Market.objects.all()
    
    # Price statistics
    stats = None
    if product_filter:
        product = get_object_or_404(Product, pk=product_filter)
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
    
    context = {
        'prices': prices,
        'products': products,
        'markets': markets,
        'current_product': product_filter,
        'current_market': market_filter,
        'current_date_range': date_filter,
        'current_search': search or '',
        'stats': stats,
        'date_range_choices': [
            ('1', 'Today'),
            ('7', 'Last 7 days'),
            ('30', 'Last 30 days'),
            ('90', 'Last 3 months'),
        ],
    }
    
    return render(request, 'market/price_list.html', context)


def price_comparison_view(request):
    """
    Compare prices across different markets for the same product.
    
    Handles GET requests to display price comparisons:
    - product: Product ID to compare prices for
    
    Returns:
        Price comparison page showing the latest prices (within last 7 days)
        for the selected product across all markets, enabling farmers to
        identify the best market for selling their produce
    """
    products = Product.objects.all()
    selected_product = None
    price_data = []
    
    product_id = request.GET.get('product')
    if product_id:
        selected_product = get_object_or_404(Product, pk=product_id)
        
        # Get recent prices for this product across all markets
        recent_prices = MarketPrice.objects.filter(
            product=selected_product,
            date_recorded__gte=timezone.now() - timedelta(days=7)
        ).select_related('market').order_by('market__name', '-date_recorded')
        
        # Group by market and get latest price
        market_prices = {}
        for price in recent_prices:
            if price.market.id not in market_prices:
                market_prices[price.market.id] = price
        
        price_data = list(market_prices.values())
    
    context = {
        'products': products,
        'selected_product': selected_product,
        'price_data': price_data,
    }
    
    return render(request, 'market/price_comparison.html', context)
