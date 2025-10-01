"""
Views for user management, profiles, and social features.

This module handles HTTP requests for user registration, authentication,
profile management, and social networking features like following other farmers
and viewing community members.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from .forms import CustomUserCreationForm, UserProfileForm, UserUpdateForm
from .models import UserProfile, UserActivity, FarmerConnection
from forum.models import BlogPost


class CustomLoginView(LoginView):
    """
    Custom login view with activity tracking.
    
    Extends Django's LoginView to track user login activity and update
    user profile last activity timestamp. Shows welcome message on successful login.
    """
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Track login activity
        UserActivity.objects.create(
            user=self.request.user,
            activity_type='login',
            description=f'User logged in from {self.request.META.get("REMOTE_ADDR", "unknown")}'
        )
        # Update user profile activity
        if hasattr(self.request.user, 'profile'):
            self.request.user.profile.update_activity()
        messages.success(self.request, f'Welcome back, {self.request.user.first_name or self.request.user.username}!')
        return response


def register_view(request):
    """
    User registration view.
    
    Handles GET requests to display registration form and POST requests
    to create new user accounts. Creates associated UserProfile automatically
    via Django signals.
    
    Returns:
        GET: Registration form
        POST: Redirects to login page on success with confirmation message
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('users:login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})


@login_required
def dashboard_view(request):
    """
    User dashboard with personalized content.
    
    Handles GET requests to display user dashboard with:
    - Recent user activities
    - User's blog posts
    - Follower/following statistics
    - Featured posts from followed users
    
    Requires user authentication. Creates UserProfile if not exists.
    
    Returns:
        Personalized dashboard page with user content and statistics
    """
    user_profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    # Get recent activities
    recent_activities = UserActivity.objects.filter(user=request.user)[:10]
    
    # Get user's blog posts
    user_posts = BlogPost.objects.filter(author=request.user)[:5]
    
    # Get followers/following counts
    followers_count = FarmerConnection.objects.filter(following=request.user).count()
    following_count = FarmerConnection.objects.filter(follower=request.user).count()
    
    # Get featured posts from followed users
    following_users = FarmerConnection.objects.filter(
        follower=request.user
    ).values_list('following', flat=True)
    
    featured_posts = BlogPost.objects.filter(
        author__in=following_users,
        is_featured=True
    )[:3]
    
    context = {
        'user_profile': user_profile,
        'recent_activities': recent_activities,
        'user_posts': user_posts,
        'followers_count': followers_count,
        'following_count': following_count,
        'featured_posts': featured_posts,
    }
    
    return render(request, 'users/dashboard.html', context)


@login_required
def profile_edit_view(request):
    """
    Edit user profile view.
    
    Handles GET requests to display profile edit form and POST requests
    to update user information and profile details including bio, location,
    farming experience, and profile picture.
    
    Requires user authentication.
    
    Returns:
        GET: Profile edit form with current user data
        POST: Redirects to dashboard on success with confirmation message
    """
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('users:dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    
    return render(request, 'users/profile_edit.html', context)


class ProfileDetailView(DetailView):
    """
    Public profile view for viewing other users' profiles.
    
    Displays user profile information including bio, location, farming details,
    blog posts, and follower/following statistics. Shows follow button if
    viewing another user's profile while authenticated.
    """
    model = User
    template_name = 'users/profile_detail.html'
    context_object_name = 'profile_user'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = self.get_object()
        
        # Get or create profile
        user_profile, created = UserProfile.objects.get_or_create(user=profile_user)
        context['user_profile'] = user_profile
        
        # Get user's public posts
        context['user_posts'] = BlogPost.objects.filter(author=profile_user)[:10]
        
        # Check if current user follows this user
        if self.request.user.is_authenticated:
            context['is_following'] = FarmerConnection.objects.filter(
                follower=self.request.user,
                following=profile_user
            ).exists()
        
        # Get followers/following counts
        context['followers_count'] = FarmerConnection.objects.filter(following=profile_user).count()
        context['following_count'] = FarmerConnection.objects.filter(follower=profile_user).count()
        
        return context


@login_required
def follow_user_view(request, user_id):
    """
    Follow or unfollow a user.
    
    Handles POST requests to toggle follow/unfollow status for a user.
    Users cannot follow themselves. If already following, unfollows the user.
    If not following, creates a new connection.
    
    Args:
        user_id: ID of the user to follow/unfollow
    
    Requires user authentication.
    
    Returns:
        Redirects to the user's profile page with status message
    """
    user_to_follow = get_object_or_404(User, pk=user_id)
    
    if user_to_follow == request.user:
        messages.error(request, "You cannot follow yourself!")
        return redirect('users:profile', pk=user_id)
    
    connection, created = FarmerConnection.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )
    
    if created:
        messages.success(request, f'You are now following {user_to_follow.get_full_name() or user_to_follow.username}!')
    else:
        connection.delete()
        messages.info(request, f'You unfollowed {user_to_follow.get_full_name() or user_to_follow.username}.')
    
    return redirect('users:profile', pk=user_id)


@login_required
def farmers_list_view(request):
    """
    List of all farmers with filtering options.
    
    Handles GET requests to display a searchable and filterable list of farmers:
    - region: Filter by geographical region
    - farmer_type: Filter by farmer type (small, medium, large, etc.)
    - experience: Filter by farming experience level (beginner, intermediate, experienced, expert)
    - search: Search by name or crops grown
    
    Requires user authentication.
    
    Returns:
        Filtered list of farmer profiles with search and filter options
    """
    farmers = UserProfile.objects.select_related('user').all()
    
    # Filter by region
    region = request.GET.get('region')
    if region:
        farmers = farmers.filter(region=region)
    
    # Filter by farmer type
    farmer_type = request.GET.get('farmer_type')
    if farmer_type:
        farmers = farmers.filter(farmer_type=farmer_type)
    
    # Filter by experience level
    experience = request.GET.get('experience')
    if experience == 'beginner':
        farmers = farmers.filter(farming_experience__lt=2)
    elif experience == 'intermediate':
        farmers = farmers.filter(farming_experience__gte=2, farming_experience__lt=10)
    elif experience == 'experienced':
        farmers = farmers.filter(farming_experience__gte=10, farming_experience__lt=20)
    elif experience == 'expert':
        farmers = farmers.filter(farming_experience__gte=20)
    
    # Search by name or crops
    search = request.GET.get('search')
    if search:
        farmers = farmers.filter(
            models.Q(user__first_name__icontains=search) |
            models.Q(user__last_name__icontains=search) |
            models.Q(user__username__icontains=search) |
            models.Q(main_crops__icontains=search)
        )
    
    context = {
        'farmers': farmers,
        'regions': UserProfile.REGION_CHOICES,
        'farmer_types': UserProfile.FARMER_TYPE_CHOICES,
        'current_filters': {
            'region': region,
            'farmer_type': farmer_type,
            'experience': experience,
            'search': search,
        }
    }
    
    return render(request, 'users/farmers_list.html', context)
