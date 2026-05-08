"""
Endpoints:
    GET /estadisticas/docente/<id>
    GET /estadisticas/alumno/<id>
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import EstadisticaPeriodo
from .serializers import EstadisticaPeriodoSerializer
from apps.reportes.grpc_clients import (
    get_materias_alumno,
    get_promedio_alumno,
    get_asistencia_alumno_resumen,   # ← resumen (dict), no la lista
)

DEV_BYPASS_AUTH = True  # cambiar a False antes de entrega final

_perms = [AllowAny] if DEV_BYPASS_AUTH else [IsAuthenticated]


@api_view(["GET"])
@permission_classes(_perms)
def estadisticas_docente(request, docente_id):
    """Historial comparativo entre periodos para un docente."""
    qs = EstadisticaPeriodo.objects.filter(docente_id=docente_id).order_by("-snapshot_at")
    return Response({"success": True, "data": EstadisticaPeriodoSerializer(qs, many=True).data})


@api_view(["GET"])
@permission_classes(_perms)
def estadisticas_alumno(request, alumno_id):
    """Estadísticas individuales del alumno (asistencia y rendimiento)."""

    # 1. Obtener materias del alumno desde MS-3
    materias = get_materias_alumno(alumno_id)

    resultados = []
    for materia in materias:
        materia_id = materia.get("id", "")
        nombre = materia.get("nombre", "Materia desconocida")

        # 2. Obtener promedio desde MS-4 y resumen de asistencia desde MS-5
        promedio = get_promedio_alumno(materia_id, alumno_id)
        asistencia = get_asistencia_alumno_resumen(alumno_id, materia_id)

        resultados.append({
            "materia_id": materia_id,
            "materia_nombre": nombre,
            "promedio": promedio,
            "asistencia": asistencia,
        })

    return Response({
        "success": True,
        "alumno_id": alumno_id,
        "total_materias": len(resultados),
        "data": resultados,
    })