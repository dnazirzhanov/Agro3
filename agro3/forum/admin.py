from django.contrib import admin
from .models import Category, Tag, BlogPost, Comment, PostImage
from ckeditor.widgets import CKEditorWidget
from django import forms
from django.utils.html import format_html


class BlogPostAdminForm(forms.ModelForm):
    """
    Custom form for BlogPost admin with CKEditor for rich text content.
    
    Uses the 'agricultural' CKEditor configuration for specialized farming content
    with support for multiple languages.
    """
    content_en = forms.CharField(
        widget=CKEditorWidget(config_name='agricultural'),
        label='Content (English)',
        help_text="Use the image styles: Disease/Symptom Photo (red border), Pest/Insect Photo (orange border), Crop/Plant Photo (green border)"
    )
    content_ru = forms.CharField(
        widget=CKEditorWidget(config_name='agricultural'),
        label='Content (Russian - Русский)',
        required=False,
        help_text="Optional: Provide Russian translation for wider accessibility"
    )
    content_ky = forms.CharField(
        widget=CKEditorWidget(config_name='agricultural'),
        label='Content (Kyrgyz - Кыргызча)',
        required=False,
        help_text="Optional: Provide Kyrgyz translation for local farmers"
    )
    
    class Meta:
        model = BlogPost
        fields = '__all__'


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 3
    fields = ['image', 'caption', 'alt_text', 'order']
    readonly_fields = ['image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 100px; max-width: 150px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for Category model with multi-language support.
    
    Enables creation and management of blog categories with translations in
    English, Russian, and Kyrgyz for better content organization across languages.
    """
    list_display = ['name', 'slug', 'color', 'created_at']
    search_fields = ['name', 'name_en', 'name_ru', 'name_ky', 'description']
    prepopulated_fields = {'slug': ('name_en',)}
    ordering = ['name']
    
    fieldsets = (
        ('English', {
            'fields': ('name_en', 'slug', 'description_en', 'color'),
        }),
        ('Russian (Русский)', {
            'fields': ('name_ru', 'description_ru'),
            'classes': ('collapse',),
        }),
        ('Kyrgyz (Кыргызча)', {
            'fields': ('name_ky', 'description_ky'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Admin interface for Tag model with multi-language support.
    
    Allows creation and management of tags with translations for improved
    content discoverability across different language preferences.
    """
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name', 'name_en', 'name_ru', 'name_ky']
    prepopulated_fields = {'slug': ('name_en',)}
    ordering = ['name']
    
    fieldsets = (
        ('English', {
            'fields': ('name_en', 'slug'),
        }),
        ('Russian (Русский)', {
            'fields': ('name_ru',),
            'classes': ('collapse',),
        }),
        ('Kyrgyz (Кыргызча)', {
            'fields': ('name_ky',),
            'classes': ('collapse',),
        }),
    )


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    """
    Admin interface for BlogPost model with comprehensive multi-language support.
    
    Provides a rich editing experience with separate fields for English, Russian,
    and Kyrgyz content, enabling agricultural knowledge sharing across language barriers.
    Features organized fieldsets for content, media, categorization, and publishing controls.
    """
    form = BlogPostAdminForm
    inlines = [PostImageInline]
    list_display = ['title', 'author', 'category', 'publication_date', 'is_published', 'is_featured', 'views_count', 'has_media']
    list_filter = ['category', 'tags', 'is_published', 'is_featured', 'publication_date', 'created_at']
    search_fields = ['title', 'title_en', 'title_ru', 'title_ky', 'content', 'short_description']
    prepopulated_fields = {'slug': ('title_en',)}
    filter_horizontal = ['tags']
    readonly_fields = ['views_count', 'created_at', 'updated_at', 'featured_image_preview']
    date_hierarchy = 'publication_date'
    
    fieldsets = (
        ('Content - English', {
            'fields': ('title_en', 'slug', 'short_description_en', 'content_en'),
            'description': 'Primary content in English (required). Use image styles to categorize photos - Disease/Symptom (red), Pest/Insect (orange), Crop/Plant (green).'
        }),
        ('Content - Russian (Русский)', {
            'fields': ('title_ru', 'short_description_ru', 'content_ru'),
            'description': 'Optional: Russian translation for wider reach in Central Asia',
            'classes': ('collapse',)
        }),
        ('Content - Kyrgyz (Кыргызча)', {
            'fields': ('title_ky', 'short_description_ky', 'content_ky'),
            'description': 'Optional: Kyrgyz translation for local farmers',
            'classes': ('collapse',)
        }),
        ('Media', {
            'fields': ('featured_image', 'featured_image_preview', 'featured_video', 'youtube_url'),
            'description': 'Add images and videos to make your post more engaging'
        }),
        ('Categorization', {
            'fields': ('category', 'tags')
        }),
        ('Publishing', {
            'fields': ('author', 'publication_date', 'is_published', 'is_featured')
        }),
        ('Statistics', {
            'fields': ('views_count',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    ordering = ['-publication_date']
    
    def featured_image_preview(self, obj):
        if obj.featured_image:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 300px;" />',
                obj.featured_image.url
            )
        return "No featured image"
    featured_image_preview.short_description = "Featured Image Preview"
    
    def has_media(self, obj):
        has_image = bool(obj.featured_image or obj.images.exists())
        has_video = bool(obj.featured_video or obj.youtube_url)
        
        if has_image and has_video:
            return format_html('<span style="color: green;">📷 🎥</span>')
        elif has_image:
            return format_html('<span style="color: blue;">📷</span>')
        elif has_video:
            return format_html('<span style="color: red;">🎥</span>')
        return format_html('<span style="color: gray;">-</span>')
    has_media.short_description = "Media"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['blog_post', 'author', 'publication_date', 'is_agronomist_reply', 'is_approved']
    list_filter = ['is_agronomist_reply', 'is_approved', 'publication_date', 'created_at']
    search_fields = ['content', 'author__username', 'blog_post__title']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'publication_date'
    ordering = ['-publication_date']
    
    fieldsets = (
        ('Comment Details', {
            'fields': ('blog_post', 'author', 'content')
        }),
        ('Moderation', {
            'fields': ('is_approved', 'is_agronomist_reply', 'publication_date')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ['blog_post', 'caption', 'order', 'created_at', 'image_preview']
    list_filter = ['created_at', 'blog_post__category']
    search_fields = ['caption', 'alt_text', 'blog_post__title']
    ordering = ['blog_post', 'order', '-created_at']
    readonly_fields = ['created_at', 'image_preview_large']
    
    fieldsets = (
        ('Image Details', {
            'fields': ('blog_post', 'image', 'image_preview_large')
        }),
        ('Metadata', {
            'fields': ('caption', 'alt_text', 'order')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 60px; max-width: 80px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = "Preview"
    
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 300px; max-width: 400px;" />',
                obj.image.url
            )
        return "No image uploaded"
    image_preview_large.short_description = "Image Preview"