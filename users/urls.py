from django.urls import path
from . import views

app_name = 'users'  # Add namespace

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.CustomSignupView.as_view(), name='register'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
]

# filepath: c:\Users\hp\Desktop\pro\Daily_Attaks_New\users\templatetags\form_filters.py
from django import template

register = template.Library()

@register.filter
def example_filter(value):
    # Example filter logic
    return value.upper()