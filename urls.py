from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ActividadViewSet, CalificacionViewSet, importar_calificaciones, concentrado

router = DefaultRouter()
router.register(r'actividades', ActividadViewSet) # POST /actividades 
router.register(r'calificaciones', CalificacionViewSet) # POST /calificaciones 

urlpatterns = [
    path('', include(router.urls)),
    path('calificaciones/importar/', importar_calificaciones, name='importar_calificaciones'), # POST /calificaciones/importar
    path('concentrado/<str:materia_id>/', concentrado, name='concentrado_materia'), # GET /concentrado/:materiaId 
]