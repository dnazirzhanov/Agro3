from django.urls import path
from . import views

app_name = 'market'

urlpatterns = [
    path('', views.market_price_list_view, name='price_list'),
    # Price comparison functionality removed as requested
    path('market/<int:pk>/', views.market_detail_view, name='market_detail'),
]