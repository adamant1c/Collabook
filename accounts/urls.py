from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.LandingView.as_view(), name='landing'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('request-reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('verify-email/', views.VerifyEmailView.as_view(), name='verify_email'),
]
