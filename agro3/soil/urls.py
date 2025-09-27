from django.urls import path
from . import views

app_name = 'soil'

urlpatterns = [
    path('', views.soil_type_list_view, name='list'),
    path('questionnaire/', views.soil_type_questionnaire_view, name='questionnaire'),
    path('result/', views.soil_type_result_view, name='result'),
    path('<int:pk>/', views.soil_type_detail_view, name='detail'),
]