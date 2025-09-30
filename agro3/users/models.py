"""
Models for user profiles and social features.

This module provides models for extended user profiles, farmer connections
(follow/follower system), and user activity tracking for the agricultural
community platform.
"""
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


class UserProfile(models.Model):
    """
    Extended user profile with agricultural and social features.
    
    Stores additional user information beyond Django's default User model,
    including farming details, location, experience level, and social features
    like verification status and reputation score. Used for personalization
    and community networking.
    """
    FARMER_TYPE_CHOICES = [
        ('individual', 'Individual Farmer'),
        ('cooperative', 'Agricultural Cooperative'),
        ('company', 'Agricultural Company'),
        ('expert', 'Agricultural Expert/Consultant'),
    ]
    
    FARM_SIZE_CHOICES = [
        ('small', 'Small (< 5 hectares)'),
        ('medium', 'Medium (5-50 hectares)'),
        ('large', 'Large (> 50 hectares)'),
        ('none', 'No farm (Expert/Consultant)'),
    ]
    
    REGION_CHOICES = [
        ('batken_city', 'Batken City'),
        ('kyzyl_kiya', 'Kyzyl-Kiya'),
        ('sulukta', 'Sulukta'),
        ('kadamjay', 'Kadamjay'),
        ('leylek', 'Leylek'),
        ('batken_villages', 'Batken Villages'),
        ('other', 'Other Region'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Information
    phone_number = models.CharField(max_length=20, blank=True, help_text="Contact phone number")
    date_of_birth = models.DateField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, help_text="Tell us about yourself and your farming experience")
    
    # Location Information
    region = models.CharField(max_length=50, choices=REGION_CHOICES, default='batken_city')
    village_or_address = models.CharField(max_length=200, blank=True, help_text="Village name or street address")
    
    # Farming Information
    farmer_type = models.CharField(max_length=20, choices=FARMER_TYPE_CHOICES, default='individual')
    farm_size = models.CharField(max_length=20, choices=FARM_SIZE_CHOICES, default='small')
    main_crops = models.CharField(max_length=300, blank=True, help_text="Main crops you grow (comma separated)")
    farming_experience = models.PositiveIntegerField(default=0, help_text="Years of farming experience")
    
    # Social Features
    is_verified_farmer = models.BooleanField(default=False, help_text="Verified by agricultural experts")
    reputation_score = models.IntegerField(default=0, help_text="Community reputation score")
    
    # Preferences
    receive_notifications = models.BooleanField(default=True)
    receive_market_alerts = models.BooleanField(default=True)
    preferred_language = models.CharField(
        max_length=10, 
        choices=[('ky', 'Kyrgyz'), ('ru', 'Russian'), ('en', 'English')], 
        default='ky'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_farmer_type_display()}"
    
    def get_absolute_url(self):
        return reverse('users:profile', kwargs={'pk': self.user.pk})
    
    def get_full_name(self):
        return self.user.get_full_name() or self.user.username
    
    def get_experience_level(self):
        """Return experience level based on years"""
        if self.farming_experience < 2:
            return "Beginner"
        elif self.farming_experience < 10:
            return "Intermediate"
        elif self.farming_experience < 20:
            return "Experienced"
        else:
            return "Expert"
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])
    
    def get_profile_completion(self):
        """Calculate profile completion percentage"""
        fields_to_check = [
            'phone_number', 'date_of_birth', 'bio', 'village_or_address',
            'main_crops', 'farming_experience', 'avatar'
        ]
        completed_fields = 0
        
        for field in fields_to_check:
            value = getattr(self, field)
            if value and (not hasattr(value, '__len__') or len(str(value).strip()) > 0):
                completed_fields += 1
        
        # Add user fields
        if self.user.first_name:
            completed_fields += 1
        if self.user.last_name:
            completed_fields += 1
        if self.user.email:
            completed_fields += 1
        
        total_fields = len(fields_to_check) + 3  # +3 for user fields
        return round((completed_fields / total_fields) * 100)


class FarmerConnection(models.Model):
    """
    Model for farmers to connect and follow each other.
    
    Implements a social networking feature allowing users to follow other farmers
    to receive updates about their activities and blog posts. Used for building
    community connections and knowledge sharing networks.
    """
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['follower', 'following']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"


class UserActivity(models.Model):
    """
    Track user activities for analytics and dashboard.
    
    Records various user actions in the system for analytics, personalization,
    and displaying recent activity on user dashboards. Helps understand user
    engagement and platform usage patterns.
    """
    ACTIVITY_CHOICES = [
        ('login', 'Login'),
        ('post_created', 'Blog Post Created'),
        ('comment_added', 'Comment Added'),
        ('crop_viewed', 'Crop Information Viewed'),
        ('market_checked', 'Market Prices Checked'),
        ('soil_test', 'Soil Test Completed'),
        ('pest_lookup', 'Pest/Disease Lookup'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    description = models.CharField(max_length=200, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['activity_type', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"
