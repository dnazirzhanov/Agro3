from django.urls import path
from .views import chemicals_list_view

urlpatterns = [
    path('', chemicals_list_view, name='chemicals_list'),
]
