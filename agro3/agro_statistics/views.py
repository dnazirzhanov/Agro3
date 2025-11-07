from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils.translation import get_language
from .models import Statistic


def filter_statistics_by_language(statistics, language_code):
    """Filter statistics to only include those with HTML content in the specified language"""
    return [stat for stat in statistics if stat.has_translation(language_code)]


def statistics_index_view(request):
    """
    Display all published statistics as a simple list.
    
    Only shows statistics that have HTML files in the user's chosen language.
    Statistics are displayed as a list of clickable titles.
    """
    current_language = get_language()
    
    # Get all published statistics
    all_statistics = Statistic.objects.filter(is_published=True).order_by('-is_featured', '-publication_date')
    
    # Filter statistics that have translation in user's language
    statistics_with_translation = filter_statistics_by_language(all_statistics, current_language)
    
    context = {
        'statistics': statistics_with_translation,
        'current_language': current_language,
    }
    
    return render(request, 'agro_statistics/index.html', context)


def statistic_detail_view(request, slug):
    """
    Display a single statistic using uploaded HTML file content.
    
    Similar to forum post detail view - renders the HTML file directly.
    Uses the simple template for clean HTML display like forum articles.
    """
    current_language = get_language()
    
    statistic = get_object_or_404(Statistic, slug=slug, is_published=True)
    
    # Check if statistic has HTML file in user's language
    if not statistic.has_translation(current_language):
        messages.warning(request, f"This statistic is not available in your selected language.")
        return redirect('statistics:index')
    
    # Increment view count
    statistic.views_count += 1
    statistic.save(update_fields=['views_count'])
    
    # Get HTML content for current language (similar to forum)
    html_content = statistic.get_html_content_for_language(current_language)
    
    context = {
        'statistic': statistic,
        'html_content': html_content,
        'current_language': current_language,
    }
    
    return render(request, 'agro_statistics/detail_simple.html', context)