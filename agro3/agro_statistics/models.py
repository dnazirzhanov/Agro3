from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone


class Statistic(models.Model):
    """Individual statistics with multilingual HTML content"""
    title = models.CharField(max_length=300, help_text="Title of the statistic")
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    
    # Short descriptions for listing page
    short_description = models.TextField(max_length=500, blank=True, help_text="Brief description shown in the list")
    
    # Multilingual HTML file uploads for complete statistical content
    html_file_en = models.FileField(
        upload_to='statistics/html/en/', 
        blank=True, null=True,
        help_text="Complete HTML file with statistics content in English"
    )
    html_file_ru = models.FileField(
        upload_to='statistics/html/ru/', 
        blank=True, null=True,
        help_text="Complete HTML file with statistics content in Russian"
    )
    html_file_ky = models.FileField(
        upload_to='statistics/html/ky/', 
        blank=True, null=True,
        help_text="Complete HTML file with statistics content in Kyrgyz"
    )
    
    # Metadata
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    views_count = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False, help_text="Only published statistics are visible to users")
    is_featured = models.BooleanField(default=False, help_text="Featured statistics appear at the top")
    publication_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', '-publication_date', '-created_at']
        verbose_name = 'Statistic'
        verbose_name_plural = 'Statistics'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('statistics:detail', kwargs={'slug': self.slug})

    def has_translation(self, language_code):
        """Check if this statistic has content in the specified language"""
        if language_code == 'en':
            return bool(self.html_file_en)
        elif language_code == 'ru':
            return bool(self.html_file_ru)
        elif language_code == 'ky':
            return bool(self.html_file_ky)
        return False

    def get_html_file_for_language(self, language_code):
        """Get the HTML file for the specified language"""
        if language_code == 'ru' and self.html_file_ru:
            return self.html_file_ru
        elif language_code == 'ky' and self.html_file_ky:
            return self.html_file_ky
        elif language_code == 'en' and self.html_file_en:
            return self.html_file_en
        return None

    def get_html_content_for_language(self, language_code):
        """Read and return HTML content for the specified language"""
        html_file = self.get_html_file_for_language(language_code)
        if html_file:
            try:
                with html_file.open('rb') as f:
                    content = f.read()
                    return content.decode('utf-8')
            except Exception as e:
                return f"<p>Error reading HTML file: {str(e)}</p>"
        return None
