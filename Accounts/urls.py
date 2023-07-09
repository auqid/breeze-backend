"""TradingAutomation URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include

from Accounts import views

urlpatterns = [
    path("register/", views.register,
         name="register"),
    path("generate_otp_email/", views.generate_otp_email,
         name="generate_otp_email"),
    path("login/", views.login_user,
         name="login_user"),
    path("forgot_password_email/", views.forgot_password_email,
         name="forgot_password_email"),
    path("forgot_password_verify_otp_email/", views.forgot_password_verify_otp_email,
         name="forgot_password_verify_email"),
    path("forgot_password_reset_password_email/", views.forgot_password_reset_password_email,
         name="forgot_password_reset_password_email"),
    path("logout/", views.logout_user,
         name='logout_user'),
]