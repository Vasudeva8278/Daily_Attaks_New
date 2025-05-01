from django.urls import path
from . import views

urlpatterns = [
    # Article URLs
    path('', views.home, name='home'),
    path('articles/', views.article_list, name='article_list'),
    path('articles/create/', views.article_create, name='article_create'),
    path('articles/<int:pk>/', views.article_detail, name='article_detail'),
    path('articles/<int:pk>/edit/', views.article_edit, name='article_edit'),
    path('articles/<int:pk>/like/', views.like_article, name='like_article'),
    path('categories/', views.category_list, name='category_list'),
    path('tags/', views.tag_list, name='tag_list'),
]