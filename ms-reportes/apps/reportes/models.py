"""
Modelo de log de Reportes generados.

Este MS no tiene datos propios "fuente" – los obtiene vía gRPC de los demás
microservicios. Solo persiste el historial de generación para auditoría.
"""
import uuid
from django.db import models


class TipoReporte(models.TextChoices):
    CALIFICACIONES = "CALIFICACIONES", "Calificaciones finales"
    ASISTENCIAS = "ASISTENCIAS", "Concentrado de asistencias"


class FormatoReporte(models.TextChoices):
    PDF = "PDF", "PDF"
    XLS = "XLS", "Excel (XLS)"
    XLSX = "XLSX", "Excel (XLSX)"


class ReporteGenerado(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo = models.CharField(max_length=20, choices=TipoReporte.choices)
    formato = models.CharField(max_length=5, choices=FormatoReporte.choices)
    materia_id = models.CharField(max_length=64)
    generado_por_user_id = models.CharField(max_length=64)

    file_name = models.CharField(max_length=255)
    size_bytes = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reportes_generados"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["materia_id", "tipo"]),
            models.Index(fields=["generado_por_user_id"]),
        ]
