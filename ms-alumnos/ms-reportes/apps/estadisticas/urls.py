from django.urls import path
from . import views

urlpatterns = [
    path("docente/<str:docente_id>", views.estadisticas_docente, name="estadisticas-docente"),
    path("alumno/<str:alumno_id>", views.estadisticas_alumno, name="estadisticas-alumno"),
]