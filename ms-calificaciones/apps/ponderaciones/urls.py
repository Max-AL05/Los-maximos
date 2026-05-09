from django.urls import path
from .views import ponderaciones_view

urlpatterns = [
    # Quitamos la palabra 'ponderaciones/' porque ya viene desde el config/urls.py
    path('<str:materia_id>/', ponderaciones_view, name='ponderaciones_materia'),
]