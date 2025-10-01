from django.contrib import admin
from .models import Category, Tag, BlogPost, Comment, PostImage
from ckeditor.widgets import CKEditorWidget
from django import forms
from django.utils.html import format_html


class BlogPostAdminForm(forms.ModelForm):
    content = forms.CharField(
        widget=CKEditorWidget(config_name='agricultural'),
        help_text="Use the image styles: Disease/Symptom Photo (red border), Pest/Insect Photo (orange border), Crop/Plant Photo (green border)"
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
    list_display = ['name', 'slug', 'color', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
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
        ('Content', {
            'fields': ('title', 'slug', 'short_description', 'content'),
            'description': 'For agricultural content: Use image styles to categorize photos - Disease/Symptom (red), Pest/Insect (orange), Crop/Plant (green). Images will be automatically sized and formatted consistently.'
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