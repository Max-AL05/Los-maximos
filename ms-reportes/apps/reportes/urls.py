from django.urls import path
from . import views

urlpatterns = [
    path("calificaciones/<str:materia_id>", views.reporte_calificaciones, name="reporte-calificaciones"),
    path("asistencias/<str:materia_id>",    views.reporte_asistencias,    name="reporte-asistencias"),
    path("historial",                       views.historial_reportes,     name="historial-reportes"),
]
