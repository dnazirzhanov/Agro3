from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


class UserProfile(models.Model):
    FARMER_TYPE_CHOICES = [
        ('individual', 'Individual Farmer'),
        ('cooperative', 'Agricultural Cooperative'),
        ('commercial', 'Commercial Farm Enterprise'),
        ('expert', 'Agricultural Expert/Consultant'),
    ]
    
    EXPERIENCE_CHOICES = [
        ('0-1', '0-1 years (Beginner)'),
        ('1-3', '1-3 years (Novice)'),
        ('3-9', '3-9 years (Intermediate)'),
        ('9-15', '9-15 years (Experienced)'),
        ('15+', '15+ years (Expert)'),
    ]
    
# Remove old region choices - will use dynamic location system
    
    AVATAR_CHOICES = [
        ('farmer_man_1', '👨‍🌾 Male Farmer 1'),
        ('farmer_man_2', '🧑‍🌾 Male Farmer 2'),
        ('farmer_woman_1', '👩‍🌾 Female Farmer 1'),
        ('farmer_woman_2', '🧕 Female Farmer 2'),
        ('default', '👤 Default'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Information
    phone_number = models.CharField(max_length=20, blank=False, help_text="Contact phone number for other farmers to reach you")
    date_of_birth = models.DateField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    avatar_choice = models.CharField(max_length=20, choices=AVATAR_CHOICES, default='default', help_text="Choose a farmer avatar")
    bio = models.TextField(max_length=500, blank=True, help_text="Tell us about yourself and your farming experience")
    
    # Location Information - New hierarchical system  
    country = models.ForeignKey('locations.Country', on_delete=models.SET_NULL, null=True, blank=True)
    region_new = models.ForeignKey('locations.Region', on_delete=models.SET_NULL, null=True, blank=True, related_name='user_profiles')
    city = models.ForeignKey('locations.City', on_delete=models.SET_NULL, null=True, blank=True)
    # Keep old region field temporarily for migration
    region_old = models.CharField(max_length=50, blank=True, help_text="Old region field - will be removed")
    village_or_address = models.CharField(max_length=200, blank=True, help_text="Specific address, village name, or additional location details")
    
    # Farming Information
    farmer_type = models.CharField(max_length=20, choices=FARMER_TYPE_CHOICES, default='individual')
    farming_experience = models.CharField(max_length=10, choices=EXPERIENCE_CHOICES, default='0-1', help_text="Years of farming experience")
    
    # Social Features
    is_verified_farmer = models.BooleanField(default=False, help_text="Verified by agricultural experts")
    reputation_score = models.IntegerField(default=0, help_text="Community reputation score")
    
    # Reputation levels based on contribution and likes
    REPUTATION_LEVELS = [
        (0, 'New Member', 'bi-person'),
        (10, 'Active Member', 'bi-chat'),
        (25, 'Helpful Contributor', 'bi-hand-thumbs-up'),
        (50, 'Trusted Farmer', 'bi-award'),
        (100, 'Community Expert', 'bi-star'),
        (200, 'Agricultural Advisor', 'bi-mortarboard'),
    ]
    
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
    
    def get_avatar_url(self):
        """Get the appropriate avatar URL based on user's choice"""
        if self.avatar:
            return self.avatar.url
        return None  # Will use CSS-styled emoji avatars instead
    
    def get_avatar_emoji(self):
        """Get emoji avatar based on user's choice"""
        avatar_map = {
            'farmer_man_1': '👨‍🌾',
            'farmer_man_2': '🧑‍🌾', 
            'farmer_woman_1': '👩‍🌾',
            'farmer_woman_2': '🧕',
            'default': '�',
        }
        return avatar_map.get(self.avatar_choice, avatar_map['default'])
    
    def get_avatar_class(self):
        """Get CSS class for avatar styling"""
        return f'avatar-{self.avatar_choice}'
    
    def get_experience_level(self):
        """Return experience level based on experience range"""
        experience_map = {
            '0-1': 'Beginner',
            '1-3': 'Novice',
            '3-9': 'Intermediate', 
            '9-15': 'Experienced',
            '15+': 'Expert',
        }
        return experience_map.get(self.farming_experience, 'Beginner')
    
    def get_region_display(self):
        """Get full location display for backward compatibility"""
        location_parts = []
        
        if self.city:
            location_parts.append(self.city.name)
        if self.region_new:
            location_parts.append(self.region_new.name)
        if self.country:
            location_parts.append(self.country.name)
        
        if location_parts:
            return ', '.join(location_parts)
        
        # Fallback to old region system
        if self.region_old:
            return self.region_old.replace('_', ' ').title()
            
        return 'Location not specified'
    
    def get_full_location(self):
        """Get complete location string"""
        return self.get_region_display()
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])
    
    def calculate_reputation_score(self):
        """Calculate reputation score based on user activity and likes received"""
        from forum.models import Like
        
        # Get user's content
        user_posts = self.user.blog_posts.filter(is_published=True)
        user_comments = self.user.comments.filter(is_approved=True)
        
        # Calculate likes received on posts and comments
        post_likes = Like.objects.filter(blog_post__in=user_posts).count()
        comment_likes = Like.objects.filter(comment__in=user_comments).count()
        
        # Points system (keeping it simple for now)
        score = 0
        score += user_posts.count() * 2  # 2 points per post
        score += user_comments.count() * 1  # 1 point per comment
        score += post_likes * 3  # 3 points per like on post
        score += comment_likes * 2  # 2 points per like on comment
        
        # Bonus for verified farmers
        if self.is_verified_farmer:
            score += 20
        
        return score
    
    def update_reputation_score(self):
        """Update the stored reputation score"""
        self.reputation_score = self.calculate_reputation_score()
        self.save(update_fields=['reputation_score'])
    
    def get_reputation_level(self):
        """Get current reputation level based on score"""
        current_level = self.REPUTATION_LEVELS[0]  # Default to first level
        
        for threshold, title, icon in self.REPUTATION_LEVELS:
            if self.reputation_score >= threshold:
                current_level = (threshold, title, icon)
            else:
                break
        
        return {
            'threshold': current_level[0],
            'title': current_level[1],
            'icon': current_level[2],
            'score': self.reputation_score
        }
    
    def get_next_reputation_level(self):
        """Get the next reputation level to achieve"""
        current_score = self.reputation_score
        
        for threshold, title, icon in self.REPUTATION_LEVELS:
            if current_score < threshold:
                return {
                    'threshold': threshold,
                    'title': title,
                    'icon': icon,
                    'points_needed': threshold - current_score
                }
        
        # Already at max level
        return None
    
    def get_likes_received_count(self):
        """Get total number of likes received on user's content"""
        from forum.models import Like
        user_posts = self.user.blog_posts.filter(is_published=True)
        user_comments = self.user.comments.filter(is_approved=True)
        
        post_likes = Like.objects.filter(blog_post__in=user_posts).count()
        comment_likes = Like.objects.filter(comment__in=user_comments).count()
        
        return post_likes + comment_likes
    
    def get_profile_completion(self):
        """Calculate profile completion percentage"""
        fields_to_check = [
            'phone_number', 'date_of_birth', 'bio', 'village_or_address',
            'farming_experience', 'avatar'
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
    """Model for farmers to connect and follow each other"""
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['follower', 'following']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"


class UserActivity(models.Model):
    """Track user activities for analytics and dashboard"""
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
