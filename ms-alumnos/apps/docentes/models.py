"""Modelo de Docente."""
import uuid
from django.db import models


class Docente(models.Model):
    """
    Docente importado desde el directorio institucional.

    El user_id es el ID del usuario en MS-1 Auth (cuando se le crea credencial).
    No se hace FK porque están en BDs separadas.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre_completo = models.CharField(max_length=255)
    correo = models.EmailField(unique=True)
    cubiculo = models.CharField(max_length=50, blank=True, null=True)

    user_id = models.CharField(max_length=64, blank=True, null=True, unique=True)

    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "docentes"
        ordering = ["nombre_completo"]

    def __str__(self):
        return self.nombre_completo
