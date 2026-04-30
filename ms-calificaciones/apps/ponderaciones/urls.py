from django.urls import path
from . import views

urlpatterns = [
    path("<uuid:materia_id>", views.ponderaciones_view, name="ponderaciones"),
]
