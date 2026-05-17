from django.contrib import admin
from .models import ReporteGenerado


@admin.register(ReporteGenerado)
class ReporteGeneradoAdmin(admin.ModelAdmin):
    list_display = ("tipo", "formato", "materia_id", "created_at")
    list_filter = ("tipo", "formato")
