from django.urls import path
from . import views

app_name = 'statistics'

urlpatterns = [
    path('', views.statistics_index_view, name='index'),
    path('<slug:slug>/', views.statistic_detail_view, name='detail'),
]