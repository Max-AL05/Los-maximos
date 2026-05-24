"""Modelos de Alumnos e Inscripciones."""
import uuid
from django.db import models


class Alumno(models.Model):
    """Alumno importado desde Excel/CSV por el docente al inscribir su materia."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    matricula = models.CharField(max_length=20, unique=True)
    nombre_completo = models.CharField(max_length=255)
    correo = models.EmailField(unique=True)
    tipo_formacion = models.CharField(max_length=50, blank=True, null=True)

    # ID del usuario en MS-1 Auth (creado al primer registro en una materia)
    user_id = models.CharField(max_length=64, blank=True, null=True, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alumnos"
        ordering = ["matricula"]

    def __str__(self):
        return f"{self.matricula} - {self.nombre_completo}"


class InscripcionMateria(models.Model):
    """
    Relación alumno ↔ materia.

    materia_id apunta a MS-2 (no se hace FK por estar en BD separada).
    Un alumno solo puede darse de baja una vez por materia (irreversible).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name="inscripciones")
    materia_id = models.CharField(max_length=64)

    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    dado_de_baja = models.BooleanField(default=False)
    fecha_baja = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "inscripciones_materia"
        unique_together = [("alumno", "materia_id")]
        indexes = [
            models.Index(fields=["materia_id"]),
            models.Index(fields=["materia_id", "dado_de_baja"]),
        ]
