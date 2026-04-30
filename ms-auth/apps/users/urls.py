"""URLs de MS-1 Auth & Users."""
from django.urls import path
from . import views


urlpatterns = [
    path("login", views.login_view, name="login"),
    path("refresh-token", views.refresh_token_view, name="refresh-token"),
    path("forgot-password", views.forgot_password_view, name="forgot-password"),
    path("reset-password", views.reset_password_view, name="reset-password"),
    path("me", views.me_view, name="me"),
]
