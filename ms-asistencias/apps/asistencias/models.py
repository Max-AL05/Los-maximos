"""Modelo de Asistencias registradas."""
import uuid
from django.db import models

from apps.sesiones.models import Sesion


class EstadoAsistencia(models.TextChoices):
    PRESENTE = "PRESENTE", "Presente"
    RETARDO = "RETARDO", "Retardo"
    AUSENTE = "AUSENTE", "Ausente"


class Asistencia(models.Model):
    """Registro persistente de asistencia validada."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sesion = models.ForeignKey(Sesion, on_delete=models.CASCADE, related_name="asistencias")
    alumno_id = models.CharField(max_length=64)             # apunta a MS-3
    materia_id = models.CharField(max_length=64)            # redundante para queries rápidas

    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=EstadoAsistencia.choices)

    # Hash del token QR escaneado (para auditoría y anti-replay)
    qr_token_hash = models.CharField(max_length=64)

    class Meta:
        db_table = "asistencias"
        unique_together = [("sesion", "alumno_id")]   # un alumno solo cuenta una vez por sesión
        indexes = [
            models.Index(fields=["materia_id", "alumno_id"]),
            models.Index(fields=["materia_id", "fecha"]),
        ]
