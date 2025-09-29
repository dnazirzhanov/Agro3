from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.blog_index_view, name='index'),
    path('post/<slug:slug>/', views.blog_post_detail_view, name='post_detail'),
    path('post/create/', views.blog_post_create_view, name='post_create'),
    path('category/<slug:slug>/', views.blog_category_list_view, name='category'),
    path('tag/<slug:slug>/', views.blog_tag_list_view, name='tag'),
    path('comment/<int:comment_id>/edit/', views.comment_edit_view, name='comment_edit'),
    path('comment/<int:comment_id>/delete/', views.comment_delete_view, name='comment_delete'),
]