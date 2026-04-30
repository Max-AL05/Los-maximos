"""
Modelos de MS-1 Auth & Users.

Define un User personalizado con campo `role` para RBAC
(Administrador / Docente / Alumno) y un modelo PasswordResetToken
para el flujo de recuperación de contraseña.
"""
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    ADMIN = "ADMIN", "Administrador"
    DOCENTE = "DOCENTE", "Docente"
    ALUMNO = "ALUMNO", "Alumno"


class User(AbstractUser):
    """Usuario centralizado del sistema AGM."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=Role.choices)
    nombre_completo = models.CharField(max_length=255)

    # Para Docentes: cubículo institucional
    cubiculo = models.CharField(max_length=50, blank=True, null=True)

    # Para Alumnos: matrícula
    matricula = models.CharField(max_length=20, blank=True, null=True, unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "role", "nombre_completo"]

    class Meta:
        db_table = "auth_users"
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["matricula"]),
        ]

    def __str__(self):
        return f"{self.email} ({self.role})"


class PasswordResetToken(models.Model):
    """Token de un solo uso para recuperación de contraseña."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reset_tokens")
    token = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "auth_password_reset_tokens"
