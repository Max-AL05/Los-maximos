from django.contrib import admin
from .models import EstadisticaPeriodo


@admin.register(EstadisticaPeriodo)
class EstadisticaPeriodoAdmin(admin.ModelAdmin):
    list_display = ("docente_id", "materia_id", "periodo_id", "promedio_grupal", "porcentaje_asistencia")
