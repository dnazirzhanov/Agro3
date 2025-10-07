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
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView
from django.core.mail import send_mail, EmailMultiAlternatives, BadHeaderError
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
from django.views.generic import CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from .forms import CustomUserCreationForm, UserProfileForm, UserUpdateForm, CustomPasswordResetForm
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
    
    def form_invalid(self, form):
        """Add debugging for invalid login attempts."""
        logger.warning(f"Login attempt failed for form data: {form.data}")
        logger.warning(f"Form errors: {form.errors}")
        logger.warning(f"Non-field errors: {form.non_field_errors()}")
        
        # Add user-friendly error message
        messages.error(self.request, 'Invalid username or password. Please try again.')
        return super().form_invalid(form)
    
    def form_valid(self, form):
        """Handle successful login with activity tracking."""
        logger.info(f"Successful login attempt for user: {form.get_user().username}")
        
        response = super().form_valid(form)
        
        # Track login activity
        try:
            UserActivity.objects.create(
                user=self.request.user,
                activity_type='login',
                description=f'User logged in from {self.request.META.get("REMOTE_ADDR", "unknown")}'
            )
        except Exception as e:
            logger.warning(f"Failed to track login activity: {e}")
        
        # Update user profile activity
        try:
            if hasattr(self.request.user, 'profile'):
                self.request.user.profile.update_activity()
        except Exception as e:
            logger.warning(f"Failed to update user profile activity: {e}")
        
        messages.success(self.request, f'Welcome back, {self.request.user.first_name or self.request.user.username}!')
        return response


class CustomLogoutView(LogoutView):
    """
    Custom logout view with activity tracking and success message.
    
    Extends Django's LogoutView to track user logout activity and provide
    user feedback with proper redirect handling for multilingual setup.
    Handles both GET (shows confirmation) and POST (performs logout) requests.
    """
    template_name = 'users/logout.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Handle both GET and POST requests properly."""
        
        # If GET request, show confirmation page
        if request.method == 'GET':
            if not request.user.is_authenticated:
                # User is not logged in, redirect to home
                return redirect('home')
            
            # Show logout confirmation page
            return render(request, self.template_name, {
                'user': request.user
            })
        
        # If POST request, proceed with logout
        elif request.method == 'POST':
            # Track logout activity before logging out
            if request.user.is_authenticated:
                try:
                    UserActivity.objects.create(
                        user=request.user,
                        activity_type='logout',
                        description=f'User logged out from {request.META.get("REMOTE_ADDR", "unknown")}'
                    )
                except Exception as e:
                    logger.warning(f'Failed to track logout activity: {e}')
            
            # Perform the logout using parent class
            response = super().dispatch(request, *args, **kwargs)
            
            # Add success message after logout
            messages.success(request, 'You have been successfully logged out.')
            
            return response
        
        # For any other method, use parent class behavior
        return super().dispatch(request, *args, **kwargs)


class CustomPasswordResetView(PasswordResetView):
    """Enhanced password reset view with username and email verification.

    Requires both username and email to match an existing user account
    before sending password reset email. Adds better security and 
    user verification.
    """
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    subject_template_name = 'users/password_reset_subject.txt'
    success_url = '/users/password-reset/done/'
    token_generator = default_token_generator
    html_email_template_name = None
    form_class = CustomPasswordResetForm

    def get_from_email(self):
        """Get the from email address with proper fallback."""
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
        if not from_email:
            from_email = getattr(settings, 'EMAIL_HOST_USER', 'noreply@agro3.com')
        return from_email

    def get_domain_and_protocol(self):
        # Prefer Site framework if installed later; for now derive from request
        request = self.request
        host = request.get_host()
        # If running locally with 0.0.0.0 include http, else assume https in production
        if host.startswith('localhost') or host.startswith('127.') or host.startswith('0.'):
            protocol = 'http'
        else:
            protocol = 'https' if not settings.DEBUG else 'http'
        return host, protocol

    def get_context_data(self, **kwargs):
        """Add extra context for email templates."""
        context = super().get_context_data(**kwargs)
        domain, protocol = self.get_domain_and_protocol()
        context.update({
            'domain': domain,
            'protocol': protocol,
            'site_name': 'Agro3 - Agricultural Platform',
        })
        return context

    def form_valid(self, form):
        """Override to add logging with username and email verification."""
        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')
        users = list(form.get_users(email))
        
        if not users:
            logger.warning("Password reset requested for non-matching username/email: %s/%s", username, email)
        else:
            for user in users:
                logger.info("Password reset email will be sent to %s/%s (user id=%s)", username, email, user.id)
        
        try:
            # Use parent class implementation which handles template rendering properly
            response = super().form_valid(form)
            if users:
                logger.info("Password reset email processing completed for %s/%s", username, email)
            return response
        except Exception as e:
            logger.exception("Error during password reset email processing for %s/%s: %s", username, email, e)
            # Re-raise the exception to show the error to the user
            raise


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
            
            # Create or update user profile with additional fields
            profile, created = UserProfile.objects.get_or_create(user=user)
            profile.phone_number = form.cleaned_data.get('phone_number')
            profile.whatsapp_number = form.cleaned_data.get('whatsapp_number')
            profile.farmer_type = form.cleaned_data.get('farmer_type')
            profile.farming_experience = form.cleaned_data.get('farming_experience')
            profile.country = form.cleaned_data.get('country')
            profile.region_new = form.cleaned_data.get('region')
            profile.village_or_address = form.cleaned_data.get('city', '').strip()  # Save city text here
            profile.avatar_choice = form.cleaned_data.get('avatar_choice')
            profile.save()
            
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
    
    # Get likes received count
    likes_received_count = user_profile.get_likes_received_count()
    
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
        'likes_received_count': likes_received_count,
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
    Follow or unfollow a user with smart redirect handling.
    
    Handles requests to toggle follow/unfollow status for a user.
    Users cannot follow themselves. If already following, unfollows the user.
    If not following, creates a new connection.
    
    Supports both regular redirects and AJAX requests for real-time updates.
    """
    from django.http import JsonResponse
    from django.urls import reverse
    
    user_to_follow = get_object_or_404(User, pk=user_id)
    
    if user_to_follow == request.user:
        error_msg = "You cannot follow yourself!"
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': error_msg}, status=400)
        messages.error(request, error_msg)
        return redirect('users:profile', pk=user_id)
    
    connection, created = FarmerConnection.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )
    
    if created:
        action = 'followed'
        is_following = True
        message = f'You are now following {user_to_follow.get_full_name() or user_to_follow.username}!'
        messages.success(request, message)
    else:
        connection.delete()
        action = 'unfollowed'
        is_following = False
        message = f'You unfollowed {user_to_follow.get_full_name() or user_to_follow.username}.'
        messages.info(request, message)
    
    # Handle AJAX requests for real-time updates
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Get updated follower count
        follower_count = FarmerConnection.objects.filter(following=user_to_follow).count()
        
        return JsonResponse({
            'success': True,
            'action': action,
            'is_following': is_following,
            'follower_count': follower_count,
            'message': message,
            'button_html': f'''
                <i class="bi bi-{'check-circle-fill' if is_following else 'person-plus'}"></i> 
                {'Following' if is_following else 'Follow'}
            '''
        })
    
    # Handle regular form submissions with smart redirects
    next_url = request.GET.get('next')
    referer = request.META.get('HTTP_REFERER', '')
    
    # If came from farmers list, redirect back with current filters
    if next_url == 'farmers_list' or 'farmers/' in referer:
        # Preserve search filters in redirect
        query_params = request.GET.copy()
        if 'next' in query_params:
            del query_params['next']
        
        redirect_url = reverse('users:farmers_list')
        if query_params:
            redirect_url += '?' + query_params.urlencode()
        return redirect(redirect_url)
    
    # Default: redirect to profile page
    return redirect('users:profile', pk=user_id)


@login_required
def farmers_list_view(request):
    """
    Enhanced farmers list with location-based filtering and fuzzy name search.
    
    Features:
    - Mandatory country/region cascading dropdowns
    - Optional fuzzy name search with typo tolerance
    - Experience and farmer type filtering
    - Follow/unfollow functionality
    - Clickable profile cards
    """
    from django.db.models import Q
    from locations.models import Country, Region, City
    from difflib import SequenceMatcher
    
    farmers = UserProfile.objects.select_related('user', 'country', 'region_new', 'city').all()
    
    # Get filter parameters
    country_id = request.GET.get('country')
    region_id = request.GET.get('region')
    farmer_type = request.GET.get('farmer_type')
    experience = request.GET.get('experience')
    search = request.GET.get('search', '').strip()
    
    # Optional country filter
    if country_id:
        farmers = farmers.filter(country_id=country_id)
        
        # Optional region filter (only if country is selected)
        if region_id:
            farmers = farmers.filter(region_new_id=region_id)
    
    # Filter by farmer type
    if farmer_type:
        farmers = farmers.filter(farmer_type=farmer_type)
    
    # Filter by experience level
    if experience == 'beginner':
        farmers = farmers.filter(farming_experience__in=['0-1'])
    elif experience == 'novice':
        farmers = farmers.filter(farming_experience__in=['1-3'])
    elif experience == 'intermediate':
        farmers = farmers.filter(farming_experience__in=['3-9'])
    elif experience == 'experienced':
        farmers = farmers.filter(farming_experience__in=['9-15'])
    elif experience == 'expert':
        farmers = farmers.filter(farming_experience__in=['15+'])
    
    # Enhanced fuzzy name search
    if search:
        # Direct search first (exact matches get priority)
        direct_matches = farmers.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__username__icontains=search) |
            Q(bio__icontains=search)
        )
        
        # If no direct matches and search is for a name, try fuzzy matching
        if not direct_matches.exists() and len(search) >= 3:
            fuzzy_matches = []
            all_farmers = farmers.all()
            
            for farmer in all_farmers:
                full_name = farmer.get_full_name().lower()
                username = farmer.user.username.lower()
                search_lower = search.lower()
                
                # Calculate similarity scores
                name_similarity = SequenceMatcher(None, search_lower, full_name).ratio()
                username_similarity = SequenceMatcher(None, search_lower, username).ratio()
                
                # Include if similarity is above threshold (0.6 = 60% similar)
                if name_similarity >= 0.6 or username_similarity >= 0.6:
                    fuzzy_matches.append((farmer, max(name_similarity, username_similarity)))
            
            # Sort by similarity score (descending)
            fuzzy_matches.sort(key=lambda x: x[1], reverse=True)
            fuzzy_farmer_ids = [farmer.id for farmer, _ in fuzzy_matches]
            
            if fuzzy_farmer_ids:
                farmers = farmers.filter(id__in=fuzzy_farmer_ids)
                # Preserve similarity order
                farmers = sorted(farmers, key=lambda f: fuzzy_farmer_ids.index(f.id))
            else:
                farmers = farmers.none()  # No matches found
        else:
            farmers = direct_matches
    
    # Exclude current user from the list
    farmers = farmers.exclude(user=request.user)
    
    # Prepare farmers data for template (simplified - no follow data needed)
    farmers_with_data = []
    for farmer in farmers:
        # Only get follower count for display, but no follow status needed
        follower_count = FarmerConnection.objects.filter(following=farmer.user).count()
        
        farmers_with_data.append({
            'profile': farmer,
            'follower_count': follower_count,
        })
    
    # Get location data for dropdowns
    countries = Country.objects.all().order_by('name')
    regions = Region.objects.none()  # Empty by default
    
    if country_id:
        regions = Region.objects.filter(country_id=country_id).order_by('name')
    
    context = {
        'farmers': farmers_with_data,
        'countries': countries,
        'regions': regions,
        'farmer_types': UserProfile.FARMER_TYPE_CHOICES,
        'current_filters': {
            'country': country_id,
            'region': region_id,
            'farmer_type': farmer_type,
            'experience': experience,
            'search': search,
        }
    }
    
    return render(request, 'users/farmers_list.html', context)


@login_required
def get_regions_by_country(request):
    """
    AJAX endpoint to get regions for a selected country.
    Used for cascading dropdowns in farmers search.
    """
    from django.http import JsonResponse
    from locations.models import Region
    
    country_id = request.GET.get('country_id')
    if not country_id:
        return JsonResponse({'regions': []})
    
    regions = Region.objects.filter(country_id=country_id).order_by('name')
    regions_data = [
        {'id': region.id, 'name': region.name}
        for region in regions
    ]
    
    return JsonResponse({'regions': regions_data})


@login_required
def ajax_follow_user(request, user_id):
    """
    AJAX endpoint for follow/unfollow functionality.
    Returns JSON response with updated follow status and counts.
    """
    from django.http import JsonResponse
    
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    user_to_follow = get_object_or_404(User, pk=user_id)
    
    if user_to_follow == request.user:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)
    
    connection, created = FarmerConnection.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )
    
    if not created:
        # Already following, so unfollow
        connection.delete()
        is_following = False
        action = 'unfollowed'
        message = f'You unfollowed {user_to_follow.get_full_name() or user_to_follow.username}'
    else:
        # New follow
        is_following = True
        action = 'followed'
        message = f'You are now following {user_to_follow.get_full_name() or user_to_follow.username}'
    
    # Get updated follower count
    follower_count = FarmerConnection.objects.filter(following=user_to_follow).count()
    
    return JsonResponse({
        'success': True,
        'is_following': is_following,
        'action': action,
        'message': message,
        'follower_count': follower_count,
        'user_id': user_id
    })
