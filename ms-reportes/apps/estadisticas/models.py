"""
Caché de estadísticas históricas por periodo.

Se llena cuando se cierra una materia y se consulta para comparativas
entre periodos. Acelera las queries sin depender de otros MS en cada request.
"""
import uuid
from django.db import models


class EstadisticaPeriodo(models.Model):
    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    docente_id = models.CharField(max_length=64)
    periodo_id = models.CharField(max_length=64)
    materia_id = models.CharField(max_length=64)

    total_alumnos         = models.IntegerField(default=0)
    aprobados             = models.IntegerField(default=0)
    reprobados            = models.IntegerField(default=0)
    promedio_grupal       = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    porcentaje_asistencia = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    snapshot_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table       = "estadisticas_periodo"
        unique_together = [("docente_id", "periodo_id", "materia_id")]
        indexes = [
            models.Index(fields=["docente_id", "periodo_id"]),
            models.Index(fields=["materia_id"]),
        ]

    def __str__(self):
        return f"Docente {self.docente_id} | {self.periodo_id} | {self.materia_id}"