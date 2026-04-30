from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, PasswordResetToken


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("email", "role", "nombre_completo", "is_active")
    list_filter = ("role", "is_active")
    search_fields = ("email", "nombre_completo", "matricula")
    ordering = ("email",)


admin.site.register(PasswordResetToken)
