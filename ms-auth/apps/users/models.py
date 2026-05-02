"""
Modelos de MS-1 Auth & Users.

Define un User personalizado con campo `role` para RBAC
(Administrador / Docente / Alumno) y un modelo PasswordResetToken
para el flujo de recuperación de contraseña.

Usa AbstractBaseUser + PermissionsMixin (en lugar de AbstractUser)
porque no necesitamos el campo `username` heredado: el email es
nuestro identificador único.
"""
import uuid
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class Role(models.TextChoices):
    ADMIN = "ADMIN", "Administrador"
    DOCENTE = "DOCENTE", "Docente"
    ALUMNO = "ALUMNO", "Alumno"


class UserManager(BaseUserManager):
    """
    Manager personalizado.

    Necesario porque el modelo no usa `username`, sino `email` como
    identificador. Sin esto, `createsuperuser` y `User.objects.create_user`
    no funcionan correctamente.
    """
    use_in_migrations = True

    def _create_user(self, email, password, role, nombre_completo, **extra):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            role=role,
            nombre_completo=nombre_completo,
            **extra,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self, email, password=None, role=Role.ALUMNO, nombre_completo="", **extra
    ):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, password, role, nombre_completo, **extra)

    def create_superuser(self, email, password=None, **extra):
        """
        Llamado por `python manage.py createsuperuser`.

        Crea un Administrador con privilegios de Django admin.
        """
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        nombre_completo = extra.pop("nombre_completo", "Administrador")
        if extra.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")
        return self._create_user(email, password, Role.ADMIN, nombre_completo, **extra)


class User(AbstractBaseUser, PermissionsMixin):
    """Usuario centralizado del sistema AGM."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=Role.choices)
    nombre_completo = models.CharField(max_length=255)

    # Para Docentes: cubículo institucional
    cubiculo = models.CharField(max_length=50, blank=True, null=True)

    # Para Alumnos: matrícula (NULL para Admin/Docente; PostgreSQL permite
    # múltiples NULLs en columna unique)
    matricula = models.CharField(max_length=20, blank=True, null=True, unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)        # acceso al /admin

    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nombre_completo"]   # campos pedidos por createsuperuser

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
