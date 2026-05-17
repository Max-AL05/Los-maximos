"""
Endpoints:
    GET /estadisticas/docente/<id>
    GET /estadisticas/alumno/<id>
"""
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import ReporteGenerado
from .serializers import ReporteGeneradoSerializer
from . import services
from .grpc_clients import get_materias_alumno, get_promedio_alumno, get_asistencia_alumno

DEV_BYPASS_AUTH = True

_perms = [AllowAny] if DEV_BYPASS_AUTH else [IsAuthenticated]


def _serve(tipo, materia_id, formato, user_id):
    formato = formato.upper()
    fn = services.REGISTRO.get((tipo, formato))
    if not fn:
        return Response(
            {"success": False, "message": f"Formato '{formato}' no soportado. Usa: PDF, XLS, XLSX"},
            status=400
        )
    try:
        file_bytes, filename, mime = fn(materia_id)
    except Exception as e:
        return Response(
            {"success": False, "message": f"Error al generar el reporte: {str(e)}"},
            status=500
        )

    ReporteGenerado.objects.create(
        tipo=tipo,
        formato=formato,
        materia_id=str(materia_id),
        generado_por_user_id=str(user_id) if user_id else "dev",
        file_name=filename,
        size_bytes=len(file_bytes),
    )

    response = HttpResponse(file_bytes, content_type=mime)
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@api_view(["GET"])
@permission_classes(_perms)
def reporte_calificaciones(request, materia_id):
    formato = request.query_params.get("formato", "pdf")
    return _serve("CALIFICACIONES", materia_id, formato, getattr(request.user, "id", None))


@api_view(["GET"])
@permission_classes(_perms)
def reporte_asistencias(request, materia_id):
    formato = request.query_params.get("formato", "pdf")
    return _serve("ASISTENCIAS", materia_id, formato, getattr(request.user, "id", None))


@api_view(["GET"])
@permission_classes(_perms)
def historial_reportes(request):
    limit = int(request.query_params.get("limit", 20))
    qs = ReporteGenerado.objects.all()[:limit]
    return Response({"success": True, "data": ReporteGeneradoSerializer(qs, many=True).data})  # FIX 1: eliminado }) suelto


@api_view(["GET"])
@permission_classes(_perms)
def estadisticas_docente(request, docente_id):
    """
    GET /estadisticas/docente/<docente_id>
    Estadísticas del docente: promedio y asistencia por materia que imparte.
    """
    # FIX 4: vista faltante implementada
    materias = services.get_materias_docente(docente_id)

    resultados = []
    for materia in materias:
        materia_id = materia.get("id", "")
        nombre     = materia.get("nombre", "Materia desconocida")

        alumnos    = services.get_alumnos_materia(materia_id)
        total_alumnos = len(alumnos)

        promedios  = [services.get_promedio_alumno(materia_id, a["id"]) for a in alumnos]
        promedio_grupo = round(sum(promedios) / total_alumnos, 2) if total_alumnos else 0

        resultados.append({
            "materia_id":     materia_id,
            "materia_nombre": nombre,
            "total_alumnos":  total_alumnos,
            "promedio_grupo": promedio_grupo,
        })

    return Response({
        "success":        True,
        "docente_id":     docente_id,
        "total_materias": len(resultados),
        "data":           resultados,
    })


@api_view(["GET"])
@permission_classes(_perms)
def estadisticas_alumno(request, alumno_id):
    """
    GET /estadisticas/alumno/<alumno_id>
    Estadísticas individuales del alumno: promedio y asistencia por materia.
    Llama a MS-3 (materias), MS-4 (promedios) y MS-5 (asistencias) vía gRPC.
    """
    materias = get_materias_alumno(alumno_id)  # FIX 2: ahora importada correctamente

    resultados = []
    for materia in materias:
        materia_id = materia.get("id", "")
        nombre     = materia.get("nombre", "Materia desconocida")

        promedio   = get_promedio_alumno(materia_id, alumno_id)   # FIX 2
        regs       = get_asistencia_alumno(alumno_id, materia_id) # FIX 2

        total     = len(regs)
        presentes = sum(1 for r in regs if r["estado"] == "PRESENTE")
        retardos  = sum(1 for r in regs if r["estado"] == "RETARDO")
        ausentes  = sum(1 for r in regs if r["estado"] == "AUSENTE")
        pct_asist = round((presentes + retardos) / total * 100, 1) if total else 0

        resultados.append({
            "materia_id":     materia_id,
            "materia_nombre": nombre,
            "promedio":       promedio,
            "asistencia": {
                "total_sesiones": total,
                "presentes":      presentes,
                "retardos":       retardos,
                "ausentes":       ausentes,
                "porcentaje":     pct_asist,
            },
        })

    return Response({
        "success":        True,
        "alumno_id":      alumno_id,
        "total_materias": len(resultados),
        "data":           resultados,
    })
# FIX 3: eliminado "que eszta mal}" al final del archivo