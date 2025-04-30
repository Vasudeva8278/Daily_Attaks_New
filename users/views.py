from django.shortcuts import render
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from allauth.account.views import SignupView
from allauth.account.forms import LoginForm, SignupForm

# Create your views here.

class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return '/'

class CustomSignupView(SignupView):
    template_name = 'users/register.html'
    form_class = SignupForm

    def get_success_url(self):
        return '/'
