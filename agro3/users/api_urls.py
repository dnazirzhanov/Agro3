from rest_framework import routers
from django.urls import path, include
from . import api_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = routers.DefaultRouter()
# You can register user/profile endpoints here if needed

urlpatterns = [
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Add registration, login, logout, password reset endpoints as needed
    path('', include(router.urls)),
]
