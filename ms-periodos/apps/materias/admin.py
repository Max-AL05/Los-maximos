from django.contrib import admin
from .models import Materia


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ("nrc", "nombre", "seccion", "periodo", "estado")
    list_filter = ("estado", "periodo")
    search_fields = ("nrc", "nombre", "clave")
