from django.urls import path
from . import views

urlpatterns = [
    path("registrar", views.registrar_asistencia, name="registrar-asistencia"),
    path("<uuid:materia_id>/hoy", views.asistencias_hoy, name="asistencias-hoy"),
    path("<uuid:materia_id>/historial", views.asistencias_historial, name="asistencias-historial"),
]
