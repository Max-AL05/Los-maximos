from django.urls import path
from . import views

urlpatterns = [
    path("bienvenida", views.bienvenida, name="bienvenida"),
    path("baja", views.baja, name="baja"),
    path("cierre-materia", views.cierre_materia, name="cierre-materia"),
    path("reset-password", views.reset_password, name="reset-password"),
]
