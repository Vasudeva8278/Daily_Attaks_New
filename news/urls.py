from django.urls import path
from . import views

urlpatterns = [
   
    # Article URLs
    path('', views.article_list, name='article_list'),
    path('create/', views.article_create, name='article_create'),
    path('<int:pk>/', views.article_detail, name='article_detail'),
    path('<int:pk>/edit/', views.article_edit, name='article_edit'),
]