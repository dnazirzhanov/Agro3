from django.contrib import admin
from .models import Category, Tag, BlogPost, Comment
from ckeditor.widgets import CKEditorWidget
from django import forms


class BlogPostAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())
    
    class Meta:
        model = BlogPost
        fields = '__all__'


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
    list_display = ['title', 'author', 'category', 'publication_date', 'is_published', 'is_featured', 'views_count']
    list_filter = ['category', 'tags', 'is_published', 'is_featured', 'publication_date', 'created_at']
    search_fields = ['title', 'content', 'short_description']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    date_hierarchy = 'publication_date'
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'short_description', 'content', 'featured_image')
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
