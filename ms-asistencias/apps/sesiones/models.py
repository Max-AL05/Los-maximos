"""Modelos de Sesiones de asistencia."""
import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone


class EstadoSesion(models.TextChoices):
    ACTIVA = "ACTIVA", "Activa"
    CERRADA = "CERRADA", "Cerrada"


class Sesion(models.Model):
    """
    Sesión de pase de lista de 10 minutos.

    Datos volátiles relacionados (cuántos alumnos han escaneado en vivo,
    set de matrículas ya escaneadas para anti-duplicado) se guardan en
    Redis con TTL = 600s. Solo el cierre persiste el resumen aquí.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    materia_id = models.CharField(max_length=64)            # apunta a MS-2
    docente_id = models.CharField(max_length=64)            # apunta a MS-1

    inicio = models.DateTimeField(default=timezone.now)
    duracion_minutos = models.IntegerField(default=10)
    umbral_retardo_min = models.IntegerField(default=5)     # presente <5min, retardo 5-10min

    estado = models.CharField(
        max_length=10,
        choices=EstadoSesion.choices,
        default=EstadoSesion.ACTIVA,
    )

    class Meta:
        db_table = "sesiones"
        indexes = [
            models.Index(fields=["materia_id", "estado"]),
            models.Index(fields=["docente_id"]),
        ]

    @property
    def fin(self):
        return self.inicio + timedelta(minutes=self.duracion_minutos)

    def __str__(self):
        return f"Sesión {self.id} ({self.estado})"
