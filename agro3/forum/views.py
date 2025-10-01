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
from .models import BlogPost, Category, Tag, Comment, Like


def blog_index_view(request):
    """Display all published blog posts with search and filtering."""
    posts = BlogPost.objects.filter(is_published=True).select_related('author', 'category').prefetch_related('tags')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        posts = posts.filter(
            Q(title__icontains=search) | 
            Q(content__icontains=search) |
            Q(short_description__icontains=search)
        )
    
    # Category filter
    category_slug = request.GET.get('category')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    
    # Tag filter
    tag_slug = request.GET.get('tag')
    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)

    # Author filter (for dashboard deep link)
    author_id = request.GET.get('author')
    if author_id:
        posts = posts.filter(author_id=author_id)
    
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    # Get featured posts
    featured_posts = BlogPost.objects.filter(is_published=True, is_featured=True)[:3]
    
    # Get categories and tags for sidebar
    categories = Category.objects.all()
    popular_tags = Tag.objects.all()[:10]
    
    context = {
        'posts': posts,
        'featured_posts': featured_posts,
        'categories': categories,
        'popular_tags': popular_tags,
        'current_search': search or '',
        'current_category': category_slug,
        'current_tag': tag_slug,
        'current_author': author_id,
    }
    
    return render(request, 'forum/index.html', context)


def blog_post_detail_view(request, slug):
    """Display a single blog post with comments and replies."""
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    
    # Increment view count
    post.views_count += 1
    post.save(update_fields=['views_count'])
    
    # Get threaded comments using the model method
    comments = post.get_threaded_comments()
    
    # Handle comment/reply submission
    if request.method == 'POST' and request.user.is_authenticated:
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        
        if content:
            parent_comment = None
            if parent_id:
                try:
                    parent_comment = Comment.objects.get(
                        id=parent_id, 
                        blog_post=post, 
                        is_approved=True
                    )
                except Comment.DoesNotExist:
                    parent_comment = None
            
            Comment.objects.create(
                blog_post=post,
                author=request.user,
                content=content,
                parent_comment=parent_comment
            )
            
            if parent_comment:
                messages.success(request, 'Your reply has been posted successfully!')
            else:
                messages.success(request, 'Your comment has been posted successfully!')
                
            return redirect('forum:post_detail', slug=post.slug)
    
    # Get related posts
    related_posts = BlogPost.objects.filter(
        is_published=True,
        category=post.category
    ).exclude(pk=post.pk)[:4]
    
    # Check if current user has liked this post
    user_has_liked_post = False
    if request.user.is_authenticated:
        user_has_liked_post = post.is_liked_by(request.user)
    
    # Add liked status to comments for the current user
    comment_likes = {}
    if request.user.is_authenticated:
        # Get all comments for this post (including replies)
        all_comments = Comment.objects.filter(blog_post=post, is_approved=True)
        
        # Create a function to recursively add like status
        def add_like_status_to_comments(comment_queryset):
            for comment in comment_queryset:
                comment.user_has_liked = comment.is_liked_by(request.user)
                comment_likes[comment.id] = comment.user_has_liked
                # Add like status to replies if they exist
                if hasattr(comment, 'replies'):
                    add_like_status_to_comments(comment.replies.all())
        
        # Add like status to top-level comments and their replies
        add_like_status_to_comments(comments)
    
    context = {
        'post': post,
        'comments': comments,
        'related_posts': related_posts,
        'user_has_liked_post': user_has_liked_post,
        'comment_likes': comment_likes if request.user.is_authenticated else {},
    }
    
    return render(request, 'forum/post_detail.html', context)


def blog_category_list_view(request, slug):
    """
    Display posts filtered by category.
    
    Handles GET requests to show all published posts within a specific category
    with pagination (10 posts per page).
    
    Args:
        slug: Category slug identifier
    
    Returns:
        Paginated list of posts in the specified category
    """
    category = get_object_or_404(Category, slug=slug)
    posts = BlogPost.objects.filter(
        is_published=True,
        category=category
    ).select_related('author').prefetch_related('tags')
    
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    context = {
        'posts': posts,
        'category': category,
        'page_title': f'Posts in {category.name}',
    }
    
    return render(request, 'forum/post_list_by_category.html', context)


def blog_tag_list_view(request, slug):
    """
    Display posts filtered by tag.
    
    Handles GET requests to show all published posts tagged with a specific tag
    with pagination (10 posts per page).
    
    Args:
        slug: Tag slug identifier
    
    Returns:
        Paginated list of posts with the specified tag
    """
    tag = get_object_or_404(Tag, slug=slug)
    posts = BlogPost.objects.filter(
        is_published=True,
        tags=tag
    ).select_related('author', 'category').prefetch_related('tags')
    
    # Pagination
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    context = {
        'posts': posts,
        'tag': tag,
        'page_title': f'Posts tagged with "{tag.name}"',
    }
    
    return render(request, 'forum/post_list_by_tag.html', context)


class BlogPostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = BlogPost
        fields = ['title', 'short_description', 'content', 'featured_image', 'category', 'tags', 'is_published']


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
