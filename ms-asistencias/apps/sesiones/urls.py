from django.urls import path
from . import views

urlpatterns = [
    path("iniciar", views.iniciar_sesion, name="iniciar-sesion"),
    path("<uuid:sesion_id>/cerrar", views.cerrar_sesion, name="cerrar-sesion"),
]
