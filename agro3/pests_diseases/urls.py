from django.urls import path
from . import views

app_name = 'pests_diseases'

urlpatterns = [
    path('', views.pest_disease_list_view, name='list'),
    path('dose-calculator/', views.dose_calculator_view, name='dose_calculator'),
    path('<int:pk>/', views.pest_disease_detail_view, name='detail'),
]