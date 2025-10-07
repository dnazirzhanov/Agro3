from django.urls import path
from . import views

app_name = 'agro_supplies'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('shops/', views.shop_list, name='shop_list'),
    path('shops/<int:pk>/', views.shop_detail, name='shop_detail'),
    path('price-comparison/', views.price_comparison, name='price_comparison'),
    path('calculator/', views.price_calculator, name='calculator'),
    path('api/product-prices/<int:product_id>/', views.get_product_prices, name='get_product_prices'),
]