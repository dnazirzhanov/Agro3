from django.urls import path
from . import views

app_name = 'crops'

urlpatterns = [
    path('', views.crop_list_view, name='list'),
    path('<int:pk>/', views.crop_detail_view, name='detail'),
]