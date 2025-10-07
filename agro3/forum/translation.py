"""
Translation configuration for forum models.

Registers translatable fields for multi-language content support (English, Russian, Kyrgyz).
This enables admin users to provide content in multiple languages for better accessibility
across Central Asian regions.
"""
from modeltranslation.translator import register, TranslationOptions
from .models import BlogPost, Category, Tag


@register(BlogPost)
class BlogPostTranslationOptions(TranslationOptions):
    """
    Define translatable fields for BlogPost model.
    
    Title, description, content, and HTML files will be available in English, Russian, and Kyrgyz.
    This allows agricultural content to be accessible to farmers in their native language.
    """
    fields = ('title', 'short_description', 'content', 'html_file')
    required_languages = ('en',)  # English is required, others optional


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    """
    Define translatable fields for Category model.
    
    Category names and descriptions will be available in multiple languages
    for better content organization and discoverability.
    """
    fields = ('name', 'description')
    required_languages = ('en',)


@register(Tag)
class TagTranslationOptions(TranslationOptions):
    """
    Define translatable fields for Tag model.
    
    Tag names will be available in multiple languages for improved searchability
    and content classification across language barriers.
    """
    fields = ('name',)
    required_languages = ('en',)
