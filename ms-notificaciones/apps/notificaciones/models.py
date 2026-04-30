"""
Modelo de Notificación.

Cada llamada al MS-6 (sea desde REST o desde gRPC) genera un registro
auditable. El campo `payload` guarda el contexto usado para renderizar
la plantilla, útil para reenvíos manuales y debugging.
"""
import uuid
from django.db import models


class TipoNotificacion(models.TextChoices):
    BIENVENIDA = "BIENVENIDA", "Bienvenida con clave única"
    BAJA = "BAJA", "Aviso de baja al docente"
    CIERRE_MATERIA = "CIERRE_MATERIA", "Cierre de materia"
    RESET_PASSWORD = "RESET_PASSWORD", "Recuperación de contraseña"


class EstadoEnvio(models.TextChoices):
    PENDIENTE = "PENDIENTE", "Pendiente"
    ENVIADO = "ENVIADO", "Enviado"
    FALLIDO = "FALLIDO", "Fallido"


class Notificacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo = models.CharField(max_length=20, choices=TipoNotificacion.choices)

    destinatario_email = models.EmailField()
    destinatario_user_id = models.CharField(max_length=64, blank=True, null=True)

    asunto = models.CharField(max_length=255)

    # Contexto serializado usado para renderizar la plantilla
    payload = models.JSONField(default=dict)

    # Cuerpo final renderizado (para auditoría)
    cuerpo_html = models.TextField(blank=True)

    estado = models.CharField(
        max_length=10,
        choices=EstadoEnvio.choices,
        default=EstadoEnvio.PENDIENTE,
    )
    error = models.TextField(blank=True)
    intentos = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "notificaciones"
        indexes = [
            models.Index(fields=["tipo", "estado"]),
            models.Index(fields=["destinatario_email"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"{self.tipo} → {self.destinatario_email} ({self.estado})"
