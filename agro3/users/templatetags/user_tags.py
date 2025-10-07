from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def user_avatar(user):
    """
    Get user avatar with fallback handling.
    Returns the user's avatar (emoji or HTML icon) or a default Bootstrap icon if no profile exists.
    """
    try:
        if hasattr(user, 'profile') and user.profile:
            return user.profile.get_avatar_display()
        else:
            return mark_safe('<i class="bi bi-person-circle"></i>')
    except Exception:
        # Fallback to Bootstrap person icon if anything fails
        return mark_safe('<i class="bi bi-person-circle"></i>')

@register.filter
def user_display_name(user):
    """
    Get user's display name with fallback handling.
    Returns full name or username with proper handling.
    """
    try:
        if user.get_full_name():
            return user.get_full_name()
        else:
            return user.username
    except Exception:
        return "User"