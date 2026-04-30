from django.urls import path
from . import views


urlpatterns = [
    path("importar/<uuid:materia_id>", views.importar_alumnos, name="importar-alumnos"),
    path("materia/<uuid:materia_id>", views.alumnos_por_materia, name="alumnos-por-materia"),
    path("<uuid:alumno_id>/baja", views.baja_alumno, name="baja-alumno"),
]
