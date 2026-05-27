from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'actividades', views.ActividadViewSet, basename='actividades')
router.register(r'calificaciones', views.CalificacionViewSet, basename='calificaciones')

urlpatterns = [
    # Esta va ANTES del router y con prefijo explícito para evitar colisión
    path('importar-calificaciones/', views.importar_calificaciones, name='importar-calificaciones'),
    path('concentrado/<uuid:materia_id>/', views.concentrado, name='concentrado'),
    path('', include(router.urls)),
]