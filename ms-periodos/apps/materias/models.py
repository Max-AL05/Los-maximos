import uuid
from django.db import models

from apps.periodos.models import Periodo


class EstadoMateria(models.TextChoices):
    ABIERTA = "ABIERTA", "Abierta"
    CERRADA = "CERRADA", "Cerrada"
    FINALIZADA = "FINALIZADA", "Finalizada (lista impresa)"


class Materia(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    periodo = models.ForeignKey(Periodo, on_delete=models.PROTECT, related_name="materias")

    nrc = models.CharField(max_length=20)
    nombre = models.CharField(max_length=255)
    seccion = models.CharField(max_length=10)
    clave = models.CharField(max_length=20)
    horario = models.CharField(max_length=255)            # Lun-Mié 10:00-12:00
    docente_id = models.CharField(max_length=64)

    estado = models.CharField(
        max_length=20,
        choices=EstadoMateria.choices,
        default=EstadoMateria.ABIERTA,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "materias"
        unique_together = [("periodo", "nrc", "seccion")]
        indexes = [
            models.Index(fields=["docente_id"]),
            models.Index(fields=["periodo", "estado"]),
        ]

    def __str__(self):
        return f"{self.nrc} {self.nombre} (sec {self.seccion})"
