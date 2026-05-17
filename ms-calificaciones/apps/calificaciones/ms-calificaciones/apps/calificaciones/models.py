"""
Modelos de actividades y calificaciones.

Mantenemos los modelos como POPOs de Django sin lógica de estatus
duplicada — esa regla vive en `apps.calificaciones.services` y se
comparte entre REST, gRPC y serializers.
"""
import uuid

from django.db import models

from apps.ponderaciones.models import Ponderacion


class Actividad(models.Model):
    """Actividad concreta dentro de una categoría (ej. 'Examen Parcial 1')."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ponderacion = models.ForeignKey(
        Ponderacion, on_delete=models.CASCADE, related_name="actividades"
    )
    nombre = models.CharField(max_length=255)
    fecha = models.DateField(blank=True, null=True)
    valor_maximo = models.DecimalField(max_digits=5, decimal_places=2, default=10)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "actividades"
        ordering = ["fecha", "nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.ponderacion.nombre})"


class Calificacion(models.Model):
    """Calificación de un alumno en una actividad concreta."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actividad = models.ForeignKey(
        Actividad, on_delete=models.CASCADE, related_name="calificaciones"
    )
    alumno_id = models.CharField(max_length=64)              # apunta a MS-3
    valor = models.DecimalField(max_digits=5, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "calificaciones"
        unique_together = [("actividad", "alumno_id")]
        indexes = [
            models.Index(fields=["alumno_id"]),
            models.Index(fields=["actividad", "alumno_id"]),
        ]

    def __str__(self):
        return f"{self.alumno_id} – {self.actividad.nombre}: {self.valor}"