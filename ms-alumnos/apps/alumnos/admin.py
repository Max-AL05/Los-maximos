from django.contrib import admin
from .models import Alumno, InscripcionMateria


@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ("matricula", "nombre_completo", "correo")
    search_fields = ("matricula", "nombre_completo", "correo")


@admin.register(InscripcionMateria)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ("alumno", "materia_id", "dado_de_baja", "fecha_inscripcion")
    list_filter = ("dado_de_baja",)
