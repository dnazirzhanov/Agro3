from django.urls import path
from . import views

app_name = 'market'

urlpatterns = [
    path('', views.market_price_list_view, name='price_list'),
    path('compare/', views.price_comparison_view, name='price_comparison'),
    path('market/<int:pk>/', views.market_detail_view, name='market_detail'),
]