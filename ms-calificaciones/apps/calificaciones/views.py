"""
Endpoints:
    POST /actividades
    POST /calificaciones                (individual)
    POST /calificaciones/importar       (Excel masivo)
    GET  /concentrado/<materia_id>      (promedios reales y redondeados)
"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Actividad, Calificacion
from .serializers import (
    ActividadSerializer,
    CalificacionSerializer,
    ImportarCalificacionesSerializer,
)


class ActividadViewSet(viewsets.ModelViewSet):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer


class CalificacionViewSet(viewsets.ModelViewSet):
    queryset = Calificacion.objects.all()
    serializer_class = CalificacionSerializer


@api_view(["POST"])
@parser_classes([MultiPartParser])
@permission_classes([IsAuthenticated])
def importar_calificaciones(request):
    """Importa calificaciones desde Excel."""
    serializer = ImportarCalificacionesSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    # TODO: parsear Excel, hacer upsert por (actividad_id, alumno_id)
    return Response({"success": True, "data": {"importadas": 0}, "message": "TODO"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def concentrado(request, materia_id):
    """
    GET /concentrado/<materia_id>

    Calcula el promedio ponderado real y redondeado para cada alumno.
    Regla de redondeo institucional:
        fracción >= 0.5 → al entero superior
        fracción <  0.5 → al entero inferior
    """
    # TODO:
    # 1. Llamar gRPC a MS-3 GetAlumnosByMateria(materia_id)
    # 2. Para cada alumno, obtener sus calificaciones agrupadas por ponderación
    # 3. Aplicar promedio ponderado: Σ (promedio_categoria * porcentaje / 100)
    # 4. Redondear según regla institucional
    return Response({"success": True, "data": [], "message": "TODO"})
