"""
Endpoints:
    GET /estadisticas/docente/<id>
    GET /estadisticas/alumno/<id>
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import EstadisticaPeriodo
from .serializers import EstadisticaPeriodoSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def estadisticas_docente(request, docente_id):
    """Historial comparativo entre periodos para un docente."""
    qs = EstadisticaPeriodo.objects.filter(docente_id=docente_id).order_by("-snapshot_at")
    return Response({"success": True, "data": EstadisticaPeriodoSerializer(qs, many=True).data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def estadisticas_alumno(request, alumno_id):
    """Estadísticas individuales del alumno (asistencia y rendimiento)."""
    # TODO:
    # 1. gRPC a MS-3 → materias del alumno
    # 2. Por cada materia: gRPC a MS-4 GetPromedioAlumno + MS-5 GetAsistenciaAlumno
    # 3. Agregar y devolver
    return Response({"success": True, "data": {}, "message": "TODO"})
