from django.shortcuts import render, redirect
from django.contrib.auth import logout
from allauth.account.views import LoginView, SignupView, LogoutView
from allauth.account.forms import LoginForm, SignupForm
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

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

class CustomLogoutView(LogoutView):
    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'You have been successfully logged out.')
            logout(request)
            request.session.flush()
        return redirect('users:login')

    def post(self, request, *args, **kwargs):
        return self.dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.dispatch(request, *args, **kwargs)
