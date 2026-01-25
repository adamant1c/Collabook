from django.shortcuts import render, redirect
from django.views.generic import FormView, View, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext as _
from core.api_client import CollabookAPI
from .forms import LoginForm, RegisterForm, PasswordResetRequestForm, PasswordResetConfirmForm

class LandingView(TemplateView):
    template_name = 'landing.html'

    def get(self, request, *args, **kwargs):
        if 'token' in request.session:
            return redirect('world:selection')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['worlds'] = CollabookAPI.list_public_stories()
        except Exception:
            context['worlds'] = []
        return context

class LoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('accounts:login')

    def get(self, request, *args, **kwargs):
        if 'token' in request.session:
            return redirect('world:selection')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        try:
            token = CollabookAPI.login(username, password)
            self.request.session['token'] = token
            self.request.session['username'] = username
            # Check if character exists and has a profession
            user = CollabookAPI.get_current_user(token)
            character = user.get('character')
            
            if character and character.get('profession'):
                return redirect('world:selection')
            else:
                return redirect('character:create')
        except Exception as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        # Name is same as username for now, as per Streamlit app
        try:
            message = CollabookAPI.register(username, email, password, name=username)
            # No auto-login!
            messages.success(self.request, _("Registration successful! Please check your email to verify your account."))
            return redirect('accounts:login')
        except Exception as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

class VerifyEmailView(View):
    def get(self, request):
        token = request.GET.get('token')
        if not token:
            messages.error(request, _("Invalid verification link."))
            return redirect('accounts:login')
            
        try:
            CollabookAPI.verify_email(token)
            messages.success(request, _("Email verified successfully! You can now login."))
        except Exception as e:
            messages.error(request, _("Verification failed: ") + str(e))
            
        return redirect('accounts:login')

class LogoutView(View):
    def get(self, request):
        request.session.flush()
        messages.info(request, _("You have been logged out."))
        return redirect('accounts:login')

class PasswordResetView(TemplateView):
    template_name = 'accounts/password_reset.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['request_form'] = PasswordResetRequestForm()
        context['confirm_form'] = PasswordResetConfirmForm()
        return context

    def post(self, request, *args, **kwargs):
        if 'request_reset' in request.POST:
            form = PasswordResetRequestForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                try:
                    CollabookAPI.request_password_reset(email)
                    messages.success(request, _("Reset link sent (check console/logs)."))
                except Exception as e:
                    messages.error(request, str(e))
            else:
                messages.error(request, _("Invalid email."))
        elif 'confirm_reset' in request.POST:
            form = PasswordResetConfirmForm(request.POST)
            if form.is_valid():
                token = form.cleaned_data['token']
                new_password = form.cleaned_data['new_password']
                try:
                    CollabookAPI.reset_password(token, new_password)
                    messages.success(request, _("Password reset successful! Please login."))
                    return redirect('accounts:login')
                except Exception as e:
                    messages.error(request, str(e))
            else:
                messages.error(request, _("Invalid data."))
        
        return self.render_to_response(self.get_context_data())
