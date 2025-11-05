from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from django.utils.html import format_html
from .models import Statistic


from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import Statistic


@admin.register(Statistic)
class StatisticAdmin(TranslationAdmin):
    """Admin interface for managing statistics with multilingual HTML file support"""
    list_display = ['title', 'is_published', 'is_featured', 'publication_date', 'views_count', 'languages_available']
    list_filter = ['is_published', 'is_featured', 'publication_date']
    search_fields = ['title', 'short_description']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'publication_date'
    ordering = ['-publication_date', 'title']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'short_description'),
        }),
        ('Publishing Options', {
            'fields': ('is_published', 'is_featured', 'publication_date'),
        }),
        ('HTML Content Files', {
            'fields': ('html_file_en', 'html_file_ru', 'html_file_ky'),
            'description': 'Upload complete HTML files containing the statistical content for each language.',
        }),
    )
    
    def languages_available(self, obj):
        """Show which languages have HTML files uploaded"""
        languages = []
        if obj.html_file_en: languages.append('EN')
        if obj.html_file_ru: languages.append('RU')
        if obj.html_file_ky: languages.append('KY')
        return ', '.join(languages) if languages else 'None'
    languages_available.short_description = 'HTML Files'
