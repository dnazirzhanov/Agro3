from django.contrib import admin
from .models import Category, Tag, BlogPost, Comment, PostImage
from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe
import logging

logger = logging.getLogger(__name__)


class SimpleRichTextWidget(forms.Textarea):
    """
    Simple rich text widget using HTML5 contenteditable with basic formatting toolbar.
    Based on Django Girls approach - simple, clean, and reliable.
    """
    
    class Media:
        css = {
            'all': ('admin/css/simple_rich_text.css',)
        }
        js = ('admin/js/simple_rich_text.js',)
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'simple-rich-text',
            'rows': 20,
            'cols': 80,
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


class SimpleRichTextFormField(forms.CharField):
    """
    Simple rich text form field that just handles HTML content directly.
    No complex JSON or delta formats - just clean HTML.
    """
    widget = SimpleRichTextWidget
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', SimpleRichTextWidget())
        super().__init__(*args, **kwargs)
    
    def to_python(self, value):
        """Convert to clean HTML."""
        if not value:
            return ''
        return str(value)



class BlogPostAdminForm(forms.ModelForm):
    """
    Multi-language blog post form with HTML file upload support.
    
    Supports English, Russian, and Kyrgyz content through both rich text editor
    and HTML file uploads for each language.
    """
    content = SimpleRichTextFormField(
        help_text="Create your agricultural content with rich text formatting (default language)",
        required=False
    )
    content_en = SimpleRichTextFormField(
        help_text="English content (rich text editor)",
        required=False
    )
    content_ru = SimpleRichTextFormField(
        help_text="Russian content (rich text editor) - Русский контент",
        required=False
    )
    content_ky = SimpleRichTextFormField(
        help_text="Kyrgyz content (rich text editor) - Кыргыз контенти",
        required=False
    )
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Check if at least one form of content is provided
        html_files = [
            cleaned_data.get('html_file'),
            cleaned_data.get('html_file_en'),
            cleaned_data.get('html_file_ru'),
            cleaned_data.get('html_file_ky')
        ]
        
        rich_text_content = [
            cleaned_data.get('content'),
            cleaned_data.get('content_en'),
            cleaned_data.get('content_ru'),
            cleaned_data.get('content_ky')
        ]
        
        has_html_content = any(html_files)
        has_rich_text = any(rich_text_content)
        
        if not has_html_content and not has_rich_text:
            raise forms.ValidationError(
                "Please provide content in at least one language using either HTML files or the rich text editor."
            )
        
        return cleaned_data
    
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
    Admin interface for Category model.
    
    Enables creation and management of blog categories for organizing agricultural content.
    """
    list_display = ['name', 'slug', 'color', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']
    
    fieldsets = (
        ('Category Details', {
            'fields': ('name', 'slug', 'description', 'color'),
        }),
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Admin interface for Tag model.
    
    Allows creation and management of tags for improved content discoverability.
    """
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']
    
    fieldsets = (
        ('Tag Details', {
            'fields': ('name', 'slug'),
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
    search_fields = ['title', 'content', 'short_description']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    readonly_fields = ['views_count', 'created_at', 'updated_at', 'featured_image_preview']
    date_hierarchy = 'publication_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug'),
            'description': 'Post title and URL slug'
        }),
        ('Multi-language Titles & Descriptions', {
            'fields': (
                ('title_en', 'short_description_en'),
                ('title_ru', 'short_description_ru'),
                ('title_ky', 'short_description_ky'),
                'short_description'
            ),
            'description': 'Titles and descriptions in different languages',
            'classes': ('collapse',)
        }),
        ('HTML File Uploads (Recommended)', {
            'fields': (
                ('html_file', 'html_file_en'),
                ('html_file_ru', 'html_file_ky')
            ),
            'description': 'Upload complete HTML files for different language versions of your post'
        }),
        ('Rich Text Editor (Alternative)', {
            'fields': ('content', 'content_en', 'content_ru', 'content_ky'),
            'description': 'Use rich text editor if not uploading HTML files',
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