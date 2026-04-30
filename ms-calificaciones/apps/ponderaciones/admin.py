from django.contrib import admin
from .models import Ponderacion


@admin.register(Ponderacion)
class PonderacionAdmin(admin.ModelAdmin):
    list_display = ("materia_id", "nombre", "porcentaje")
    search_fields = ("materia_id",)
