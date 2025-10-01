from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, FarmerConnection, UserActivity


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'farmer_type', 'region_new', 'farming_experience', 'is_verified_farmer']
    list_filter = ['farmer_type', 'region_new', 'farming_experience', 'is_verified_farmer', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'village_or_address']
    readonly_fields = ['created_at', 'updated_at', 'last_activity']
    
    fieldsets = [
        ('User', {'fields': ['user']}),
        ('Personal Information', {
            'fields': ['phone_number', 'date_of_birth', 'avatar', 'bio']
        }),
        ('Location', {
            'fields': ['country', 'region_new', 'city', 'village_or_address']
        }),
        ('Farming Information', {
            'fields': ['farmer_type', 'farming_experience']
        }),
        ('Social Features', {
            'fields': ['is_verified_farmer', 'reputation_score']
        }),
        ('Preferences', {
            'fields': ['receive_notifications', 'receive_market_alerts', 'preferred_language']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at', 'last_activity'],
            'classes': ['collapse']
        })
    ]


@admin.register(FarmerConnection)
class FarmerConnectionAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'created_at']
    list_filter = ['created_at']
    search_fields = ['follower__username', 'following__username']


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'description', 'timestamp']
    list_filter = ['activity_type', 'timestamp']
    search_fields = ['user__username', 'description']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'


# Extend the User admin to show profile info
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)


# Re-register User admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
