from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import PasswordResetToken, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):

    ordering = ("email",)
    list_display = ("email", "nombre_completo", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("email", "nombre_completo", "matricula")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Información personal", {
            "fields": ("nombre_completo", "role", "matricula", "cubiculo"),
        }),
        ("Permisos", {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
        }),
        ("Fechas", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "nombre_completo", "role",
                "matricula", "cubiculo",
                "password1", "password2",
            ),
        }),
    )
    readonly_fields = ("date_joined", "last_login")


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "expires_at", "used", "created_at")
    list_filter = ("used",)
    readonly_fields = ("created_at",)
