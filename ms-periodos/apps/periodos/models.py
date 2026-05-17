import uuid
from django.db import models


class Periodo(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)              # ej. "Primavera 2026"
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    plan_estudios = models.CharField(max_length=100)
    activo = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "periodos"
        ordering = ["-fecha_inicio"]
        constraints = [
            models.UniqueConstraint(
                fields=["activo"],
                condition=models.Q(activo=True),
                name="unique_periodo_activo",
            )
        ]

    def __str__(self):
        return self.nombre
