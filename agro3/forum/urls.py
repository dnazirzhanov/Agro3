from django.urls import path
from . import views

app_name = 'forum'

urlpatterns = [
    path('', views.blog_index_view, name='index'),
    path('post/<slug:slug>/', views.blog_post_detail_view, name='post_detail'),
    path('category/<slug:slug>/', views.blog_category_list_view, name='category'),
    path('tag/<slug:slug>/', views.blog_tag_list_view, name='tag'),
]