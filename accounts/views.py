from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages
from django.utils.translation import gettext as _
from core.api_client import CollabookAPI
from .forms import LoginForm, RegisterForm, PasswordResetRequestForm, PasswordResetConfirmForm
from asgiref.sync import sync_to_async


class LandingView(View):
    template_name = 'landing.html'

    async def get(self, request, *args, **kwargs):
        if await sync_to_async(request.session.get)('token'):
            return redirect('world:selection')
        try:
            worlds = await CollabookAPI.list_public_stories()
        except Exception:
            worlds = []
        return await sync_to_async(render)(request, self.template_name, {'worlds': worlds})


class LoginView(View):
    template_name = 'accounts/login.html'

    async def get(self, request, *args, **kwargs):
        if await sync_to_async(request.session.get)('token'):
            return redirect('world:selection')
        form = LoginForm()
        return await sync_to_async(render)(request, self.template_name, {'form': form})

    async def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                token = await CollabookAPI.login(username, password)
                await sync_to_async(request.session.__setitem__)('token', token)
                await sync_to_async(request.session.__setitem__)('username', username)
                # Check if character exists and has a profession
                user = await CollabookAPI.get_current_user(token)
                character = user.get('character')

                if character and character.get('profession'):
                    return redirect('world:selection')
                else:
                    return redirect('character:create')
            except Exception as e:
                messages.error(request, str(e))
        return await sync_to_async(render)(request, self.template_name, {'form': form})


class RegisterView(View):
    template_name = 'accounts/register.html'

    async def get(self, request, *args, **kwargs):
        form = RegisterForm()
        return await sync_to_async(render)(request, self.template_name, {'form': form})

    async def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                await CollabookAPI.register(username, email, password, name=username)
                messages.success(request, _("Registration successful! Please check your email to verify your account."))
                await sync_to_async(request.session.pop)("access_token", None)
                await sync_to_async(request.session.pop)("user", None)
                return redirect('accounts:login')
            except Exception as e:
                messages.error(request, str(e))
        return await sync_to_async(render)(request, self.template_name, {'form': form})


class VerifyEmailView(View):
    async def get(self, request):
        token = request.GET.get('token')
        if not token:
            messages.error(request, _("Invalid verification link."))
            return redirect('accounts:login')

        try:
            await CollabookAPI.verify_email(token)
            messages.success(request, _("Email verified successfully! You can now login."))
        except Exception as e:
            messages.error(request, _("Verification failed: ") + str(e))

        return redirect('accounts:login')


class LogoutView(View):
    def get(self, request):
        request.session.flush()
        messages.info(request, _("You have been logged out."))
        return redirect('accounts:login')


class PasswordResetView(View):
    template_name = 'accounts/password_reset.html'

    async def get(self, request, *args, **kwargs):
        token = request.GET.get('token', '')
        context = {
            'request_form': PasswordResetRequestForm(),
            'confirm_form': PasswordResetConfirmForm(initial={'token': token}),
            'show_confirm': bool(token),
        }
        return await sync_to_async(render)(request, self.template_name, context)

    async def post(self, request, *args, **kwargs):
        if 'request_reset' in request.POST:
            form = PasswordResetRequestForm(request.POST)
            if form.is_valid():
                email = form.cleaned_data['email']
                try:
                    await CollabookAPI.request_password_reset(email)
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
                    await CollabookAPI.reset_password(token, new_password)
                    messages.success(request, _("Password reset successful! Please login."))
                    return redirect('accounts:login')
                except Exception as e:
                    messages.error(request, str(e))
            else:
                messages.error(request, _("Invalid data."))

        token = request.GET.get('token', '')
        context = {
            'request_form': PasswordResetRequestForm(),
            'confirm_form': PasswordResetConfirmForm(initial={'token': token}),
            'show_confirm': bool(token),
        }
        return await sync_to_async(render)(request, self.template_name, context)
