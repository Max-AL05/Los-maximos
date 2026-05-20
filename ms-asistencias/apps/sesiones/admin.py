from django.contrib import admin
from .models import Sesion


@admin.register(Sesion)
class SesionAdmin(admin.ModelAdmin):
    list_display = ("id", "materia_id", "docente_id", "inicio", "estado")
    list_filter = ("estado",)
