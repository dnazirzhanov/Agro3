"""
Models for the agricultural forum/blog system.

This module provides models for managing blog posts, categories, tags, and comments,
enabling farmers and agricultural experts to share knowledge, ask questions, and
discuss farming topics.
"""
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator
# Removed django_quill dependency - using simple TextField for content
import os


class Category(models.Model):
    """
    Represents blog post categories for organizing agricultural content.
    
    Categories help organize posts by topics such as crop management, market prices,
    pest control, etc. Each category has a unique color for visual identification.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default='#007bff', help_text='Hex color code')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('forum:category', kwargs={'slug': self.slug})


class Tag(models.Model):
    """
    Represents tags for blog posts, enabling detailed content classification.
    
    Tags provide additional categorization beyond categories, allowing posts to be
    tagged with multiple relevant keywords for better searchability.
    """
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('forum:tag', kwargs={'slug': self.slug})


def get_post_image_path(instance, filename):
    """Generate upload path for blog post images"""
    return f'blog/posts/{instance.slug}/{filename}'


def get_post_video_path(instance, filename):
    """Generate upload path for blog post videos"""
    return f'blog/videos/{instance.slug}/{filename}'


def get_post_html_path(instance, filename):
    """Generate upload path for blog post HTML files"""
    return f'blog/html/{instance.slug}/{filename}'


class BlogPost(models.Model):
    """
    Represents a blog post in the agricultural knowledge-sharing forum.
    
    Blog posts allow users to share farming knowledge, experiences, and advice.
    Supports rich text content, images, categorization, tagging, and features
    like view counts and publication control.
    """
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_posts'
    )
    publication_date = models.DateTimeField(default=timezone.now)
    short_description = models.CharField(max_length=300, blank=True, null=True)
    content = models.TextField(blank=True, null=True, help_text="Rich text content")
    
    # HTML file upload for blog content (modeltranslation will create language variants)
    html_file = models.FileField(
        upload_to=get_post_html_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['html', 'htm'])],
        help_text='Upload an HTML file for the blog post content'
    )
    
    featured_image = models.ImageField(
        upload_to='blog/featured/', 
        blank=True, 
        null=True,
        help_text='Main image for the post (recommended: 1200x630px)'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts'
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    
    # Video support
    featured_video = models.FileField(
        upload_to=get_post_video_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'webm', 'ogg'])],
        help_text='Upload a video file (MP4, WebM, or OGG format, max 50MB)'
    )
    youtube_url = models.URLField(
        blank=True,
        null=True,
        help_text='YouTube video URL (alternative to uploaded video)'
    )
    
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-publication_date']
        indexes = [
            models.Index(fields=['-publication_date', 'is_published']),
            models.Index(fields=['slug']),
            models.Index(fields=['category', '-publication_date']),
            models.Index(fields=['is_featured', 'is_published']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('forum:post_detail', kwargs={'slug': self.slug})
    
    def get_title_for_language(self, language_code='en'):
        """Get title for specific language, falling back to default title."""
        if language_code == 'ru' and hasattr(self, 'title_ru') and self.title_ru:
            return self.title_ru
        elif language_code == 'ky' and hasattr(self, 'title_ky') and self.title_ky:
            return self.title_ky
        elif language_code == 'en' and hasattr(self, 'title_en') and self.title_en:
            return self.title_en
        return self.title  # Fallback to default title
    
    def get_description_for_language(self, language_code='en'):
        """Get description for specific language, falling back to default description."""
        if language_code == 'ru' and hasattr(self, 'short_description_ru') and self.short_description_ru:
            return self.short_description_ru
        elif language_code == 'ky' and hasattr(self, 'short_description_ky') and self.short_description_ky:
            return self.short_description_ky
        elif language_code == 'en' and hasattr(self, 'short_description_en') and self.short_description_en:
            return self.short_description_en
        return self.short_description  # Fallback to default description
    
    def get_html_file_for_language(self, language_code='en'):
        """Get HTML file for specific language, falling back to default file."""
        if language_code == 'ru' and hasattr(self, 'html_file_ru') and self.html_file_ru:
            return self.html_file_ru
        elif language_code == 'ky' and hasattr(self, 'html_file_ky') and self.html_file_ky:
            return self.html_file_ky
        return self.html_file  # Fallback to default HTML file
    
    def has_translation(self, language_code):
        """Check if post has content in specific language."""
        if language_code == 'ru':
            html_file_ru = getattr(self, 'html_file_ru', None)
            title_ru = getattr(self, 'title_ru', None)
            return bool(html_file_ru or title_ru)
        elif language_code == 'ky':
            html_file_ky = getattr(self, 'html_file_ky', None)
            title_ky = getattr(self, 'title_ky', None)
            return bool(html_file_ky or title_ky)
        elif language_code == 'en':
            html_file_en = getattr(self, 'html_file_en', self.html_file)
            title_en = getattr(self, 'title_en', self.title)
            return bool(html_file_en or title_en)
        return False
    
    def get_comment_count(self):
        return self.comments.filter(is_approved=True).count()
    
    def get_youtube_embed_id(self):
        """Extract YouTube video ID from URL for embedding"""
        if not self.youtube_url:
            return None
        
        # Handle different YouTube URL formats
        url = self.youtube_url
        if 'youtu.be/' in url:
            return url.split('youtu.be/')[1].split('?')[0]
        elif 'youtube.com/watch?v=' in url:
            return url.split('v=')[1].split('&')[0]
        elif 'youtube.com/embed/' in url:
            return url.split('embed/')[1].split('?')[0]
        return None
    
    def has_video(self):
        """Check if post has any video content"""
        return bool(self.featured_video or self.youtube_url)
    
    def get_primary_image(self):
        """Get the main image for display - featured image or first additional image"""
        if self.featured_image:
            return self.featured_image
        first_image = self.images.first()
        return first_image.image if first_image else None
    
    def get_gallery_images(self):
        """Get all additional images for gallery display"""
        return self.images.all().order_by('order', 'created_at')
    
    def get_threaded_comments(self):
        """Get all top-level comments with their replies in a tree structure"""
        return self.comments.filter(is_approved=True, parent_comment=None).prefetch_related('replies')
    
    def get_like_count(self):
        """Get total number of likes for this post"""
        return self.likes.count()
    
    def is_liked_by(self, user):
        """Check if a specific user has liked this post"""
        if user.is_anonymous:
            return False
        return self.likes.filter(user=user).exists()
    
    def get_html_content(self):
        """Get HTML content from uploaded file or fall back to QuillField content"""
        if self.html_file:
            try:
                with self.html_file.open('r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                # Log the error and fall back to content field
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error reading HTML file for post {self.id}: {e}")
        
        # Fall back to QuillField content
        return str(self.content) if self.content else ""
    
    def has_html_file(self):
        """Check if the post has an uploaded HTML file"""
        return bool(self.html_file)
    
    def get_html_file_for_language(self, language_code='en'):
        """Get the appropriate HTML file based on language preference"""
        if language_code == 'ru' and hasattr(self, 'html_file_ru') and self.html_file_ru:
            return self.html_file_ru
        elif language_code == 'ky' and hasattr(self, 'html_file_ky') and self.html_file_ky:
            return self.html_file_ky
        elif hasattr(self, 'html_file_en') and self.html_file_en:
            return self.html_file_en
        elif self.html_file:
            return self.html_file
        return None
    
    def get_html_content_for_language(self, language_code='en'):
        """Get HTML content for specific language, extracting only body content"""
        content, _ = self.get_html_and_styles_for_language(language_code)
        return content
    
    def get_extracted_styles_for_language(self, language_code='en'):
        """Get CSS styles from HTML file for specific language"""
        _, styles = self.get_html_and_styles_for_language(language_code)
        return styles
    
    def get_html_and_styles_for_language(self, language_code='en'):
        """Get both HTML content and CSS styles for specific language in one read"""
        html_file = self.get_html_file_for_language(language_code)
        if html_file:
            try:
                content = html_file.read().decode('utf-8')
                html_file.close()
                
                # If this is a complete HTML document, extract body content and styles
                if '<!DOCTYPE html>' in content or '<html' in content:
                    import re
                    
                    # Extract styles from head section
                    extracted_styles = None
                    head_match = re.search(r'<head[^>]*>(.*?)</head>', content, re.DOTALL | re.IGNORECASE)
                    if head_match:
                        head_content = head_match.group(1)
                        style_matches = re.findall(r'<style[^>]*>(.*?)</style>', head_content, re.DOTALL | re.IGNORECASE)
                        if style_matches:
                            # Combine all styles
                            combined_styles = '\n'.join(style_matches)
                            # Remove problematic styles that interfere with our layout
                            combined_styles = re.sub(r'body\s*\{[^}]*\}', '', combined_styles, flags=re.IGNORECASE)
                            combined_styles = re.sub(r'html\s*\{[^}]*\}', '', combined_styles, flags=re.IGNORECASE)
                            # Remove any margin/padding on universal selectors that might break layout
                            combined_styles = re.sub(r'\*\s*\{[^}]*margin[^}]*\}', '', combined_styles, flags=re.IGNORECASE)
                            combined_styles = re.sub(r'\*\s*\{[^}]*padding[^}]*\}', '', combined_styles, flags=re.IGNORECASE)
                            
                            extracted_styles = combined_styles.strip() if combined_styles.strip() else None
                    
                    # Extract content between <body> tags
                    body_content = ""
                    body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
                    if body_match:
                        body_content = body_match.group(1).strip()
                        
                        # Remove any existing style tags from body (we already extracted them from head)
                        body_content = re.sub(r'<style[^>]*>.*?</style>', '', body_content, flags=re.DOTALL | re.IGNORECASE)
                        
                        # Remove any script tags that might cause issues
                        body_content = re.sub(r'<script[^>]*>.*?</script>', '', body_content, flags=re.DOTALL | re.IGNORECASE)
                    else:
                        # If no body tag found, try to extract content inside html tag
                        html_match = re.search(r'<html[^>]*>(.*?)</html>', content, re.DOTALL | re.IGNORECASE)
                        if html_match:
                            body_content = html_match.group(1)
                            # Remove head section
                            body_content = re.sub(r'<head[^>]*>.*?</head>', '', body_content, flags=re.DOTALL | re.IGNORECASE)
                            # Remove any remaining style tags
                            body_content = re.sub(r'<style[^>]*>.*?</style>', '', body_content, flags=re.DOTALL | re.IGNORECASE)
                    
                    return body_content.strip(), extracted_styles
                else:
                    # If it's just HTML fragments, return as is with no styles
                    return content, None
                    
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error reading HTML file for post {self.id} (lang: {language_code}): {e}")
        
        # Fallback to regular content field
        fallback_content = str(self.content) if self.content else f"<p>No content available in {language_code}.</p>"
        return fallback_content, None


class Comment(models.Model):
    """
    Represents comments and replies on blog posts.
    
    Enables discussion on blog posts through a hierarchical comment system.
    Supports nested replies, approval moderation, and special marking for
    agricultural expert responses.
    """
    blog_post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    content = models.TextField()
    publication_date = models.DateTimeField(default=timezone.now)
    is_agronomist_reply = models.BooleanField(
        default=False,
        help_text='Mark if this comment is from an agricultural expert'
    )
    is_approved = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['publication_date']
        indexes = [
            models.Index(fields=['blog_post', 'is_approved', 'parent_comment']),
            models.Index(fields=['author', '-publication_date']),
        ]
    
    def __str__(self):
        return f'Comment by {self.author.username} on {self.blog_post.title}'
    
    def get_absolute_url(self):
        return f"{self.blog_post.get_absolute_url()}#comment-{self.id}"
    
    def is_reply(self):
        return self.parent_comment is not None
    
    def get_reply_count(self):
        return self.replies.filter(is_approved=True).count()
    
    def get_thread_depth(self):
        """Calculate the depth of this comment in the thread"""
        depth = 0
        parent = self.parent_comment
        while parent:
            depth += 1
            parent = parent.parent_comment
        return depth
    
    def get_root_comment(self):
        """Get the top-level comment of this thread"""
        if not self.parent_comment:
            return self
        parent = self.parent_comment
        while parent.parent_comment:
            parent = parent.parent_comment
        return parent
    
    def get_all_descendants(self):
        """Get all nested replies recursively"""
        descendants = []
        for reply in self.replies.filter(is_approved=True):
            descendants.append(reply)
            descendants.extend(reply.get_all_descendants())
        return descendants
    
    def get_thread_total_replies(self):
        """Get total number of replies in the entire thread"""
        return len(self.get_all_descendants())
    
    def get_like_count(self):
        """Get total number of likes for this comment"""
        return self.likes.count()
    
    def is_liked_by(self, user):
        """Check if a specific user has liked this comment"""
        if user.is_anonymous:
            return False
        return self.likes.filter(user=user).exists()


class PostImage(models.Model):
    """Additional images for blog posts"""
    blog_post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(
        upload_to=get_post_image_path,
        help_text='Additional images for the post'
    )
    caption = models.CharField(max_length=200, blank=True, help_text='Optional image caption')
    alt_text = models.CharField(max_length=200, blank=True, help_text='Alt text for accessibility')
    order = models.PositiveIntegerField(default=0, help_text='Display order')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f'Image for {self.blog_post.title}'
    
    def save(self, *args, **kwargs):
        if not self.alt_text and self.caption:
            self.alt_text = self.caption
        super().save(*args, **kwargs)


class Like(models.Model):
    """Model for tracking likes on posts and comments"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    # Generic foreign key to support both posts and comments
    blog_post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='likes'
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='likes'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Ensure a user can only like a post or comment once
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'blog_post'],
                name='unique_post_like',
                condition=models.Q(blog_post__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['user', 'comment'],
                name='unique_comment_like',
                condition=models.Q(comment__isnull=False)
            ),
        ]
        # Ensure either post or comment is set, but not both
        constraints.append(
            models.CheckConstraint(
                check=(
                    models.Q(blog_post__isnull=False, comment__isnull=True) |
                    models.Q(blog_post__isnull=True, comment__isnull=False)
                ),
                name='like_either_post_or_comment'
            )
        )
        ordering = ['-created_at']
    
    def __str__(self):
        if self.blog_post:
            return f'{self.user.username} likes post "{self.blog_post.title}"'
        elif self.comment:
            return f'{self.user.username} likes comment by {self.comment.author.username}'
        return f'Like by {self.user.username}'
    
    @property
    def content_object(self):
        """Return the liked object (post or comment)"""
        return self.blog_post or self.comment
    
    @property
    def content_author(self):
        """Return the author of the liked content"""
        if self.blog_post:
            return self.blog_post.author
        elif self.comment:
            return self.comment.author
        return None
