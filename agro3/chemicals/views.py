from django.shortcuts import render
from django.utils.translation import get_language
from .models import ChemicalProduct
from django.urls import path


# Create your views here.

def chemicals_list_view(request):
    current_language = get_language() or 'en'
    products = ChemicalProduct.objects.filter()
    # Only show products with a translation in the current language
    products = [p for p in products if getattr(p, f'name_{current_language}', None)]
    context = {
        'products': products,
        'current_language': current_language,
    }
    return render(request, 'chemicals/chemicals_list.html', context)

urlpatterns = [
    path('', chemicals_list_view, name='chemicals_list'),
]
