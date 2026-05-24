from django.contrib import admin
from .models import Docente


@admin.register(Docente)
class DocenteAdmin(admin.ModelAdmin):
    list_display = ("nombre_completo", "correo", "cubiculo", "activo")
    search_fields = ("nombre_completo", "correo")
