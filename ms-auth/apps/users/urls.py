from django.urls import path

from . import views


urlpatterns = [
    path("register", views.register_view, name="register"),
    path("login", views.LoginView.as_view(), name="login"),
    path("refresh-token", views.RefreshTokenView.as_view(), name="refresh-token"),
    path("forgot-password", views.forgot_password_view, name="forgot-password"),
    path("reset-password", views.reset_password_view, name="reset-password"),
    path("me", views.me_view, name="me"),
]
