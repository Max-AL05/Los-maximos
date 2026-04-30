from django.contrib import admin
from .models import Asistencia


@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ("alumno_id", "materia_id", "fecha", "estado")
    list_filter = ("estado",)
