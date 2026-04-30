from django.urls import path
from . import views

urlpatterns = [
    path("docente/<uuid:docente_id>", views.estadisticas_docente, name="estadisticas-docente"),
    path("alumno/<uuid:alumno_id>", views.estadisticas_alumno, name="estadisticas-alumno"),
]
