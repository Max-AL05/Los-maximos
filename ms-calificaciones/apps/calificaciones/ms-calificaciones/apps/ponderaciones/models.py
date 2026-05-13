"""Modelos de Ponderaciones (criterios de evaluación)."""
import uuid
from django.db import models
from django.core.exceptions import ValidationError

class Ponderacion(models.Model):
    def clean(self):
        # Suma los porcentajes de las otras ponderaciones de la misma materia
        total_otros = Ponderacion.objects.filter(
            materia_id=self.materia_id
        ).exclude(id=self.id).aggregate(models.Sum('porcentaje'))['porcentaje__sum'] or 0
        
        if total_otros + self.porcentaje > 100:
            raise ValidationError(
                f"La suma de ponderaciones excedería el 100% (Actual: {total_otros + self.porcentaje}%)."
            )
    """
    Categoría de evaluación con su porcentaje (ej. Exámenes 40%).

    Para una materia dada, la suma de todas las Ponderaciones debe ser
    EXACTAMENTE 100. Esta validación se hace a nivel de servicio.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    materia_id = models.CharField(max_length=64)            # apunta a MS-2
    nombre = models.CharField(max_length=100)               # ej. "Exámenes"
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2)  # ej. 40.00

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    class Meta:
        db_table = "ponderaciones"
        unique_together = [("materia_id", "nombre")]
        indexes = [models.Index(fields=["materia_id"])]

    def __str__(self):
        return f"{self.nombre} ({self.porcentaje}%)"
