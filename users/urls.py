from django.urls import path
from . import views

app_name = 'users'  # Add namespace

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.CustomSignupView.as_view(), name='register'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
]