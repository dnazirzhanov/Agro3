"""
Forum template tags for rendering content from different editors.

This module provides template filters for handling content that may come from
different rich text editors (CKEditor, Quill, etc.) and ensures proper rendering.
"""

from django import template
from django.utils.safestring import mark_safe
# Removed django_quill dependency - using simple text fields
import json
import logging

register = template.library.Library()
logger = logging.getLogger(__name__)


@register.filter
def render_blog_content(blog_post, language_code='en'):
    """
    Render blog post content for specific language, prioritizing HTML file over rich text content.
    
    Args:
        blog_post: BlogPost instance
        language_code: Language code ('en', 'ru', 'ky')
    
    Returns:
        Safe HTML string for rendering
    """
    if not blog_post:
        return mark_safe("")
    
    try:
        # Get the appropriate HTML file for the language
        html_file = blog_post.get_html_file_for_language(language_code)
        
        # First, try to get content from HTML file
        if html_file:
            try:
                with html_file.open('r', encoding='utf-8') as f:
                    html_content = f.read()
                    return mark_safe(html_content)
            except Exception as e:
                logger.warning(f"Error reading HTML file for post {blog_post.id} in {language_code}: {e}")
        
        # Fall back to rich text content for the specific language
        if language_code == 'ru' and hasattr(blog_post, 'content_ru') and blog_post.content_ru:
            return render_content(blog_post.content_ru)
        elif language_code == 'ky' and hasattr(blog_post, 'content_ky') and blog_post.content_ky:
            return render_content(blog_post.content_ky)
        elif language_code == 'en' and hasattr(blog_post, 'content_en') and blog_post.content_en:
            return render_content(blog_post.content_en)
        
        # Final fallback to default content
        return render_content(blog_post.content)
        
    except Exception as e:
        logger.error(f"Error rendering blog post content: {e}")
        return mark_safe("<p>Content could not be loaded</p>")


@register.simple_tag(takes_context=True)
def render_blog_content_with_language(context, blog_post):
    """
    Render blog post content using the current language from request context.
    
    Args:
        context: Template context (contains request)
        blog_post: BlogPost instance
    
    Returns:
        Safe HTML string for rendering
    """
    request = context.get('request')
    if request and hasattr(request, 'LANGUAGE_CODE'):
        language_code = request.LANGUAGE_CODE
    else:
        # Try to get language from URL path
        try:
            path_parts = request.path.strip('/').split('/')
            if path_parts and path_parts[0] in ['en', 'ru', 'ky']:
                language_code = path_parts[0]
            else:
                language_code = 'en'
        except:
            language_code = 'en'
    
    return render_blog_content(blog_post, language_code)


@register.filter
def get_title_for_language(blog_post, language_code='en'):
    """Get blog post title for specific language."""
    if hasattr(blog_post, 'get_title_for_language'):
        return blog_post.get_title_for_language(language_code)
    return blog_post.title


@register.filter
def get_description_for_language(blog_post, language_code='en'):
    """Get blog post description for specific language."""
    if hasattr(blog_post, 'get_description_for_language'):
        return blog_post.get_description_for_language(language_code)
    return blog_post.short_description


@register.filter
def render_content(content):
    """
    Render content from either CKEditor (HTML) or Quill (JSON Delta) format.
    Provides backward compatibility for existing CKEditor posts.
    
    Args:
        content: Either HTML string, Quill Delta JSON, or QuillField instance
    
    Returns:
        Safe HTML string for rendering
    """
    if not content:
        return mark_safe("")
    
    try:
        # Handle QuillField objects specially to avoid triggering parsing
        if hasattr(content, '__class__') and 'FieldQuill' in str(content.__class__):
            try:
                # Get the raw JSON string directly from the database field
                raw_content = content.json_string
            except Exception:
                # If that fails, get the raw value from the field
                try:
                    raw_content = content.field.value_from_object(content.instance)
                except Exception:
                    # Last resort: assume it's HTML content 
                    raw_content = "<p>Content could not be loaded</p>"
        else:
            # Convert to string to work with raw content
            raw_content = str(content)
        
        # Check if content looks like HTML (CKEditor format)
        if raw_content.strip().startswith('<') and '>' in raw_content:
            # It's HTML content from CKEditor, render as-is
            return mark_safe(raw_content)
        
        # Check if it looks like JSON (Quill Delta format)
        content_stripped = raw_content.strip()
        if content_stripped.startswith('{') and content_stripped.endswith('}'):
            try:
                # Try to parse as JSON to validate
                parsed_json = json.loads(content_stripped)
                
                # If it has 'html' key, use that directly
                if isinstance(parsed_json, dict) and 'html' in parsed_json:
                    return mark_safe(parsed_json['html'])
                
                # Otherwise try to render with Quill
                from django_quill.quill import Quill
                quill_instance = Quill(content_stripped)
                return mark_safe(quill_instance.html)
                
            except (json.JSONDecodeError, Exception) as e:
                logger.warning(f"Error parsing content as Quill JSON: {e}")
                # If JSON parsing fails, treat as plain text
                pass
        
        # If it doesn't look like HTML or JSON, treat as plain text
        # Convert newlines to <br> tags for basic formatting
        return mark_safe(raw_content.replace('\n', '<br>'))
        
    except Exception as e:
        logger.error(f"Error in render_content: {e}")
        # Ultimate fallback - avoid calling str() on QuillField
        if hasattr(content, '__class__') and 'FieldQuill' in str(content.__class__):
            return mark_safe("<p>Content could not be displayed</p>")
        return mark_safe(str(content))


@register.filter
def is_quill_content(content):
    """
    Check if content is in Quill Delta JSON format.
    
    Args:
        content: Content to check
    
    Returns:
        Boolean indicating if content is Quill format
    """
    if not content or not isinstance(content, str):
        return False
    
    content_stripped = content.strip()
    if content_stripped.startswith('{') and content_stripped.endswith('}'):
        try:
            data = json.loads(content_stripped)
            # Check if it has the structure of a Quill Delta
            return isinstance(data, dict) and ('ops' in data or 'html' in data)
        except json.JSONDecodeError:
            return False
    
    return False


@register.filter
def is_html_content(content):
    """
    Check if content is in HTML format.
    
    Args:
        content: Content to check
    
    Returns:
        Boolean indicating if content is HTML format
    """
    if not content or not isinstance(content, str):
        return False
    
    content_stripped = content.strip()
    return content_stripped.startswith('<') and '>' in content_stripped


@register.simple_tag
def debug_content_type(content):
    """
    Debug tag to help identify content type during development.
    
    Args:
        content: Content to analyze
    
    Returns:
        String describing the content type
    """
    if not content:
        return "Empty content"
    
    if hasattr(content, '__class__') and 'FieldQuill' in str(content.__class__):
        return f"QuillField instance (type: {type(content).__name__})"
    
    if isinstance(content, str):
        content_stripped = content.strip()
        if content_stripped.startswith('{') and content_stripped.endswith('}'):
            try:
                json.loads(content_stripped)
                return "JSON content (likely Quill Delta)"
            except json.JSONDecodeError:
                return "String starting with { but not valid JSON"
        
        if content_stripped.startswith('<') and content_stripped.endswith('>'):
            return "HTML content (likely CKEditor)"
        
        return f"Plain text content (length: {len(content_stripped)})"
    
    return f"Unknown content type: {type(content).__name__}"