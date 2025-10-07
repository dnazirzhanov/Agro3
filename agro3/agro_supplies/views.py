from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Avg, Min, Max, Count
from django.db import models
from django.core.paginator import Paginator
from .models import ChemicalCategory, ChemicalProduct, Shop, ChemicalPrice
from locations.models import Country, Region, City


def product_list(request):
    """List all chemical products with filtering and search - focused on pricing"""
    products = ChemicalProduct.objects.filter(is_active=True).select_related('category').prefetch_related('prices__shop')
    categories = ChemicalCategory.objects.all()
    
    # Get location options for filtering - based on shops that sell products
    countries = Country.objects.filter(shops__product_prices__product__is_active=True).distinct().order_by('name')
    regions = Region.objects.none()  # Will be populated based on country selection
    
    # Filtering
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Location filtering - filter products based on shops in selected locations
    country_id = request.GET.get('country')
    region_id = request.GET.get('region')
    
    if country_id:
        # Filter products available in the selected country
        products = products.filter(prices__shop__country_id=country_id).distinct()
        # Get regions for selected country
        regions = Region.objects.filter(country_id=country_id, shops__product_prices__product__is_active=True).distinct().order_by('name')
        
        if region_id:
            # Further filter by region
            products = products.filter(prices__shop__region_id=region_id).distinct()
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(brand__icontains=search_query) |
            Q(active_ingredient__icontains=search_query) |
            Q(target_crops__icontains=search_query)
        )
    
    # Order products with prices - prioritize products with available prices
    products = products.annotate(
        min_price=Min('prices__price'),
        price_count=models.Count('prices')
    ).order_by('-price_count', 'min_price', 'brand', 'name')
    
    # Prefetch prices with shop information for efficient querying
    products = products.prefetch_related('prices__shop__country', 'prices__shop__region', 'prices__shop__city')
    
    # Pagination
    paginator = Paginator(products, 15)  # Show 15 products per page for table display
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'countries': countries,
        'regions': regions,
        'selected_category': category_id,
        'selected_country': country_id,
        'selected_region': region_id,
        'search_query': search_query,
        'total_products': products.count()
    }
    return render(request, 'agro_supplies/product_list.html', context)


def product_detail(request, pk):
    """Detailed view of a chemical product with price comparison"""
    product = get_object_or_404(ChemicalProduct, pk=pk, is_active=True)
    
    # Get all prices for this product
    prices = ChemicalPrice.objects.filter(product=product).select_related('shop', 'shop__country', 'shop__region', 'shop__city').order_by('price')
    
    # Price statistics
    price_stats = prices.aggregate(
        min_price=Min('price'),
        max_price=Max('price'),
        avg_price=Avg('price')
    )
    
    # Filter by location if specified
    country_id = request.GET.get('country')
    region_id = request.GET.get('region') 
    city_id = request.GET.get('city')
    
    if country_id:
        prices = prices.filter(shop__country_id=country_id)
    if region_id:
        prices = prices.filter(shop__region_id=region_id)
    if city_id:
        prices = prices.filter(shop__city_id=city_id)
    
    # Location options for filtering
    countries = Country.objects.filter(shops__product_prices__product=product).distinct()
    regions = Region.objects.filter(shops__product_prices__product=product).distinct()
    cities = City.objects.filter(shops__product_prices__product=product).distinct()
    
    context = {
        'product': product,
        'prices': prices,
        'price_stats': price_stats,
        'countries': countries,
        'regions': regions,
        'cities': cities,
        'selected_country': country_id,
        'selected_region': region_id,
        'selected_city': city_id,
    }
    return render(request, 'agro_supplies/product_detail.html', context)


def shop_list(request):
    """List all shops with filtering"""
    shops = Shop.objects.filter(is_active=True).select_related('country', 'region', 'city')
    
    # Filtering
    shop_type = request.GET.get('shop_type')
    if shop_type:
        shops = shops.filter(shop_type=shop_type)
    
    country_id = request.GET.get('country')
    if country_id:
        shops = shops.filter(country_id=country_id)
    
    region_id = request.GET.get('region')
    if region_id:
        shops = shops.filter(region_id=region_id)
    
    city_id = request.GET.get('city')
    if city_id:
        shops = shops.filter(city_id=city_id)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        shops = shops.filter(
            Q(name__icontains=search_query) |
            Q(owner_name__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(shops, 10)  # Show 10 shops per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Filter options
    countries = Country.objects.filter(shops__is_active=True).distinct()
    
    # Only load regions/cities if country/region is selected (for form resubmission)
    regions = []
    cities = []
    
    if country_id:
        regions = Region.objects.filter(country_id=country_id, shops__is_active=True).distinct()
        
        if region_id:
            cities = City.objects.filter(region_id=region_id, shops__is_active=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'shop_types': Shop.SHOP_TYPES,
        'countries': countries,
        'regions': regions,
        'cities': cities,
        'selected_shop_type': shop_type,
        'selected_country': country_id,
        'selected_region': region_id,
        'selected_city': city_id,
        'search_query': search_query,
        'total_shops': shops.count()
    }
    return render(request, 'agro_supplies/shop_list.html', context)


def shop_detail(request, pk):
    """Detailed view of a shop with all products and prices"""
    shop = get_object_or_404(Shop, pk=pk, is_active=True)
    
    # Get all products sold by this shop with their prices
    prices = ChemicalPrice.objects.filter(shop=shop).select_related('product', 'product__category').order_by('product__category', 'product__name')
    
    # Filter by category if specified
    category_id = request.GET.get('category')
    if category_id:
        prices = prices.filter(product__category_id=category_id)
    
    # Search within shop products
    search_query = request.GET.get('search')
    if search_query:
        prices = prices.filter(
            Q(product__name__icontains=search_query) |
            Q(product__brand__icontains=search_query) |
            Q(product__active_ingredient__icontains=search_query)
        )
    
    # Categories available in this shop
    categories = ChemicalCategory.objects.filter(products__prices__shop=shop).distinct()
    
    # Pagination
    paginator = Paginator(prices, 15)  # Show 15 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'shop': shop,
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search_query,
        'total_products': prices.count()
    }
    return render(request, 'agro_supplies/shop_detail.html', context)


def price_comparison(request):
    """Compare prices across different shops for products"""
    products = ChemicalProduct.objects.filter(is_active=True).select_related('category')
    
    # Filtering
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Search
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(brand__icontains=search_query) |
            Q(active_ingredient__icontains=search_query)
        )
    
    # Location filtering
    country_id = request.GET.get('country')
    region_id = request.GET.get('region')
    city_id = request.GET.get('city')
    
    # Get products with their price ranges
    product_prices = []
    for product in products[:20]:  # Limit to 20 products for performance
        prices_query = ChemicalPrice.objects.filter(product=product)
        
        if country_id:
            prices_query = prices_query.filter(shop__country_id=country_id)
        if region_id:
            prices_query = prices_query.filter(shop__region_id=region_id)
        if city_id:
            prices_query = prices_query.filter(shop__city_id=city_id)
        
        price_stats = prices_query.aggregate(
            min_price=Min('price'),
            max_price=Max('price'),
            avg_price=Avg('price'),
            shop_count=prices_query.count()
        )
        
        if price_stats['min_price']:  # Only include products with prices
            product_prices.append({
                'product': product,
                'stats': price_stats
            })
    
    # Filter options
    categories = ChemicalCategory.objects.all()
    countries = Country.objects.filter(shops__product_prices__isnull=False).distinct()
    regions = Region.objects.filter(shops__product_prices__isnull=False).distinct()
    cities = City.objects.filter(shops__product_prices__isnull=False).distinct()
    
    context = {
        'product_prices': product_prices,
        'categories': categories,
        'countries': countries,
        'regions': regions,
        'cities': cities,
        'selected_category': category_id,
        'selected_country': country_id,
        'selected_region': region_id,
        'selected_city': city_id,
        'search_query': search_query,
    }
    return render(request, 'agro_supplies/price_comparison.html', context)


def price_calculator(request):
    """Chemical product price calculator"""
    products = ChemicalProduct.objects.filter(is_active=True, prices__isnull=False).distinct().select_related('category').order_by('brand', 'name')
    categories = ChemicalCategory.objects.all()
    countries = Country.objects.filter(shops__product_prices__product__is_active=True).distinct().order_by('name')
    
    context = {
        'products': products,
        'categories': categories,
        'countries': countries,
    }
    return render(request, 'agro_supplies/calculator.html', context)


def get_product_prices(request, product_id):
    """API endpoint to get prices for a specific product"""
    from django.http import JsonResponse
    
    try:
        product = ChemicalProduct.objects.get(id=product_id, is_active=True)
        prices = ChemicalPrice.objects.filter(
            product=product, 
            is_in_stock=True
        ).select_related('shop', 'shop__country', 'shop__region', 'shop__city').order_by('price')
        
        price_data = []
        for price in prices:
            price_data.append({
                'id': price.id,
                'shop_name': price.shop.name,
                'shop_location': price.shop.get_location_display(),
                'price': float(price.price),  # This is the price per package at this shop
                'currency': price.currency,
                'package_size': float(product.package_size),
                'package_unit': product.get_package_unit_display(),
            })
        
        return JsonResponse({
            'success': True,
            'product_name': f"{product.brand} {product.name}",
            'package_size': float(product.package_size),
            'package_unit': product.get_package_unit_display(),
            'prices': price_data
        })
    
    except ChemicalProduct.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Product not found'
        })
