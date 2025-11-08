"""
Views for the agricultural forum/blog system.

This module handles HTTP requests for the forum including displaying blog posts,
managing comments, filtering by categories and tags, and creating new posts.
Enables knowledge sharing and community discussion among farmers.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.utils.translation import get_language
from django import forms
# Removed django_quill dependency
from .models import BlogPost, Category, Tag, Comment, Like


def filter_posts_by_language(posts, language_code):
    """
    Filter blog posts to only include those with content in the specified language.
    
    Args:
        posts: QuerySet of BlogPost objects
        language_code: Language code (en, ru, ky)
    
    Returns:
        List of posts that have translation in the specified language
    """
    return [post for post in posts if post.has_translation(language_code)]


def filter_categories_by_language(categories, language_code):
    """
    Filter categories to only include those with names in the specified language.
    
    Args:
        categories: QuerySet of Category objects  
        language_code: Language code (en, ru, ky)
    
    Returns:
        Filtered QuerySet of categories with translation in the specified language
    """
    if language_code == 'en':
        # English is the default language, show all categories
        return categories
    
    # For non-English languages, filter categories that have translation
    field_name = f'name_{language_code}'
    return categories.filter(**{f'{field_name}__isnull': False}).exclude(**{field_name: ''})


def filter_tags_by_language(tags, language_code):
    """
    Filter tags to only include those with names in the specified language.
    
    Args:
        tags: QuerySet of Tag objects
        language_code: Language code (en, ru, ky)
    
    Returns:
        Filtered QuerySet of tags with translation in the specified language
    """
    if language_code == 'en':
        # English is the default language, show all tags
        return tags
    
    # For non-English languages, filter tags that have translation
    field_name = f'name_{language_code}'
    return tags.filter(**{f'{field_name}__isnull': False}).exclude(**{field_name: ''})


def blog_index_view(request):
    """
    Display all published blog posts with search and filtering.
    
    Only shows posts, categories, and tags that have translations in the user's chosen language.
    This ensures users only see content they can understand in their preferred language.
    """
    current_language = get_language()
    
    posts = BlogPost.objects.filter(is_published=True).select_related('author', 'category').prefetch_related('tags')

    # Search functionality (search in user's language)
    search = request.GET.get('search')
    if search:
        if current_language == 'en':
            posts = posts.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(short_description__icontains=search)
            )
        else:
            # Search in translated fields
            title_field = f'title_{current_language}__icontains'
            content_field = f'content_{current_language}__icontains'
            desc_field = f'short_description_{current_language}__icontains'
            posts = posts.filter(
                Q(**{title_field: search}) |
                Q(**{content_field: search}) |
                Q(**{desc_field: search})
            )

    # Get categories and tags with translations in user's language
    available_categories = filter_categories_by_language(Category.objects.all(), current_language)
    available_tags = filter_tags_by_language(Tag.objects.all(), current_language)

    # Category filter
    category_slug = request.GET.get('category')
    if category_slug:
        try:
            category = available_categories.get(slug=category_slug)
            posts = posts.filter(category=category)
        except Category.DoesNotExist:
            # Category doesn't have translation in user's language, ignore filter
            category_slug = None

    # Tag filter
    tag_slug = request.GET.get('tag')
    if tag_slug:
        try:
            tag = available_tags.get(slug=tag_slug)
            posts = posts.filter(tags=tag)
        except Tag.DoesNotExist:
            # Tag doesn't have translation in user's language, ignore filter
            tag_slug = None

    # Author filter (for dashboard deep link)
    author_id = request.GET.get('author')
    if author_id:
        posts = posts.filter(author_id=author_id)

    # Only show posts with a translation in the current language
    posts_with_translation = filter_posts_by_language(posts, current_language)

    # Pagination
    paginator = Paginator(posts_with_translation, 10)
    page_number = request.GET.get('page')
    paginated_posts = paginator.get_page(page_number)

    # Get featured posts (only those with translation in user's language)
    featured_posts_queryset = BlogPost.objects.filter(is_published=True, is_featured=True)
    featured_posts = filter_posts_by_language(featured_posts_queryset, current_language)[:3]

    context = {
        'posts': paginated_posts,
        'featured_posts': featured_posts,
        'categories': available_categories,
        'current_search': search or '',
        'current_category': category_slug,
        'current_tag': tag_slug,
        'current_author': author_id,
        'current_language': current_language,
    }

    return render(request, 'forum/index.html', context)


def blog_post_detail_view(request, slug):
    """
    Display a single blog post using uploaded HTML file content.
    
    Only shows the post if it has content in the user's chosen language.
    """
    current_language = get_language()
    
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    
    # Check if post has translation in user's language
    if not post.has_translation(current_language):
        # Post doesn't have content in user's language, show 404
        messages.warning(request, f"This post is not available in your selected language.")
        return redirect('forum:index')
    
    # Increment view count
    post.views_count += 1
    post.save(update_fields=['views_count'])
    
    # Get HTML content and styles for current language
    html_content = post.get_html_content_for_language(current_language)
    extracted_styles = post.get_extracted_styles_for_language(current_language)
    
    context = {
        'post': post,
        'html_content': html_content,
        'extracted_styles': extracted_styles,
        'current_language': current_language,
    }
    
    return render(request, 'forum/post_detail_simple.html', context)


def blog_category_list_view(request, slug):
    """
    Display posts filtered by category.
    
    Only shows the category and its posts if they have translations in the user's chosen language.
    
    Handles GET requests to show all published posts within a specific category
    with pagination (10 posts per page).
    
    Args:
        slug: Category slug identifier
    
    Returns:
        Paginated list of posts in the specified category
    """
    current_language = get_language()
    
    # Get categories with translations in user's language
    available_categories = filter_categories_by_language(Category.objects.all(), current_language)
    
    try:
        category = available_categories.get(slug=slug)
    except Category.DoesNotExist:
        # Category doesn't have translation in user's language, show 404
        messages.warning(request, f"This category is not available in your selected language.")
        return redirect('forum:index')
    
    posts_queryset = BlogPost.objects.filter(
        is_published=True,
        category=category
    ).select_related('author').prefetch_related('tags')
    
    # Only show posts with translation in user's language
    posts_with_translation = filter_posts_by_language(posts_queryset, current_language)
    
    # Pagination
    paginator = Paginator(posts_with_translation, 10)
    page_number = request.GET.get('page')
    paginated_posts = paginator.get_page(page_number)
    
    context = {
        'posts': paginated_posts,
        'category': category,
        'page_title': f'Posts in {category.name}',
        'current_language': current_language,
    }
    
    return render(request, 'forum/post_list_by_category.html', context)


def blog_tag_list_view(request, slug):
    """
    Display posts filtered by tag.
    
    Only shows the tag and its posts if they have translations in the user's chosen language.
    
    Handles GET requests to show all published posts tagged with a specific tag
    with pagination (10 posts per page).
    
    Args:
        slug: Tag slug identifier
    
    Returns:
        Paginated list of posts with the specified tag
    """
    current_language = get_language()
    
    # Get tags with translations in user's language
    available_tags = filter_tags_by_language(Tag.objects.all(), current_language)
    
    try:
        tag = available_tags.get(slug=slug)
    except Tag.DoesNotExist:
        # Tag doesn't have translation in user's language, show 404
        messages.warning(request, f"This tag is not available in your selected language.")
        return redirect('forum:index')
    
    posts_queryset = BlogPost.objects.filter(
        is_published=True,
        tags=tag
    ).select_related('author', 'category').prefetch_related('tags')
    
    # Only show posts with translation in user's language
    posts_with_translation = filter_posts_by_language(posts_queryset, current_language)
    
    # Pagination
    paginator = Paginator(posts_with_translation, 10)
    page_number = request.GET.get('page')
    paginated_posts = paginator.get_page(page_number)
    
    context = {
        'posts': paginated_posts,
        'tag': tag,
        'page_title': f'Posts tagged with "{tag.name}"',
        'current_language': current_language,
    }
    
    return render(request, 'forum/post_list_by_tag.html', context)


class BlogPostForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 10, 'class': 'form-control'}))

    class Meta:
        model = BlogPost
        fields = ['title', 'short_description', 'content', 'featured_image', 'category', 'tags', 'is_published']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter an engaging title for your post...'
        })
        self.fields['short_description'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Write a brief description (optional)...',
            'rows': 2
        })
        self.fields['featured_image'].widget.attrs.update({
            'class': 'form-control',
            'accept': 'image/*'
        })
        self.fields['category'].widget.attrs.update({
            'class': 'form-select'
        })
        self.fields['tags'].widget.attrs.update({
            'class': 'form-select'
        })


@login_required
def blog_post_create_view(request):
    """Create a new blog post (author is current user)."""
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post: BlogPost = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            messages.success(request, 'Your post has been created!')
            return redirect(post.get_absolute_url())
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BlogPostForm()

    return render(request, 'forum/post_form.html', {'form': form})


@login_required
def comment_edit_view(request, comment_id):
    """
    Edit a comment (only by the author).
    
    Handles POST requests to update comment content. Only the comment author
    can edit their own comments. Requires user authentication.
    
    Args:
        comment_id: ID of the comment to edit
    
    POST parameters:
        content: Updated comment text
    
    Returns:
        Redirects to the blog post detail page after editing
    """
    comment = get_object_or_404(Comment, id=comment_id, author=request.user)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            comment.content = content
            comment.save(update_fields=['content', 'updated_at'])
            messages.success(request, 'Comment updated successfully!')
        else:
            messages.error(request, 'Comment content cannot be empty.')
    
    return redirect('forum:post_detail', slug=comment.blog_post.slug)


@login_required
def comment_delete_view(request, comment_id):
    """
    Delete a comment (only by the author or admin).
    
    Handles POST requests to delete comments. Users can delete their own comments,
    and staff members can delete any comment. Requires user authentication.
    
    Args:
        comment_id: ID of the comment to delete
    
    Returns:
        Redirects to the blog post detail page after deletion
    """
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Check permissions
    if comment.author != request.user and not request.user.is_staff:
        messages.error(request, 'You can only delete your own comments.')
        return redirect('forum:post_detail', slug=comment.blog_post.slug)
    
    if request.method == 'POST':
        post_slug = comment.blog_post.slug
        comment.delete()
        messages.success(request, 'Comment deleted successfully!')
        return redirect('forum:post_detail', slug=post_slug)
    
    return redirect('forum:post_detail', slug=comment.blog_post.slug)


@login_required
def toggle_post_like(request, post_id):
    """Toggle like/unlike for a blog post"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    post = get_object_or_404(BlogPost, id=post_id, is_published=True)
    
    try:
        # Try to get existing like
        like = Like.objects.get(user=request.user, blog_post=post)
        # If exists, unlike (delete)
        like.delete()
        liked = False
        message = 'Post unliked successfully!'
    except Like.DoesNotExist:
        # If doesn't exist, create like
        Like.objects.create(user=request.user, blog_post=post)
        liked = True
        message = 'Post liked successfully!'
        
        # Update author's reputation score
        post.author.profile.update_reputation_score()
    
    like_count = post.get_like_count()
    
    # Always return JSON response for AJAX requests
    return JsonResponse({
        'success': True,
        'liked': liked,
        'like_count': like_count,
        'message': message
    })


@login_required
def toggle_comment_like(request, comment_id):
    """Toggle like/unlike for a comment"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)
    
    comment = get_object_or_404(Comment, id=comment_id, is_approved=True)
    
    try:
        # Try to get existing like
        like = Like.objects.get(user=request.user, comment=comment)
        # If exists, unlike (delete)
        like.delete()
        liked = False
        message = 'Comment unliked successfully!'
    except Like.DoesNotExist:
        # If doesn't exist, create like
        Like.objects.create(user=request.user, comment=comment)
        liked = True
        message = 'Comment liked successfully!'
        
        # Update author's reputation score
        comment.author.profile.update_reputation_score()
    
    like_count = comment.get_like_count()
    
    # Always return JSON response for AJAX requests
    return JsonResponse({
        'success': True,
        'liked': liked,
        'like_count': like_count,
        'message': message
    })
