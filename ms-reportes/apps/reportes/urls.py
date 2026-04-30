from django.urls import path
from . import views

urlpatterns = [
    path("calificaciones/<uuid:materia_id>", views.reporte_calificaciones, name="reporte-calificaciones"),
    path("asistencias/<uuid:materia_id>", views.reporte_asistencias, name="reporte-asistencias"),
]
