from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import CustomUserCreationForm

# Example: API endpoint for user profile (protected)
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = getattr(user, 'profile', None)
        data = {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'profile': {
                'phone_number': profile.phone_number if profile else '',
                'bio': profile.bio if profile else '',
            }
        }
        return Response(data)

# You can add more API endpoints for registration, password reset, etc.
