from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import BlogPost, Category, Tag, Comment


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
    }
    
    return render(request, 'forum/index.html', context)


def blog_post_detail_view(request, slug):
    """Display a single blog post with comments."""
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    
    # Increment view count
    post.views_count += 1
    post.save(update_fields=['views_count'])
    
    # Get approved comments
    comments = post.comments.filter(is_approved=True).select_related('author')
    
    # Handle comment submission
    if request.method == 'POST' and request.user.is_authenticated:
        content = request.POST.get('content')
        if content:
            Comment.objects.create(
                blog_post=post,
                author=request.user,
                content=content
            )
            messages.success(request, 'Your comment has been posted successfully!')
            return redirect('forum:post_detail', slug=post.slug)
    
    # Get related posts
    related_posts = BlogPost.objects.filter(
        is_published=True,
        category=post.category
    ).exclude(pk=post.pk)[:4]
    
    context = {
        'post': post,
        'comments': comments,
        'related_posts': related_posts,
    }
    
    return render(request, 'forum/post_detail.html', context)


def blog_category_list_view(request, slug):
    """Display posts filtered by category."""
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
    """Display posts filtered by tag."""
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
