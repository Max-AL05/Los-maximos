from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import ReporteGenerado
from .serializers import ReporteGeneradoSerializer
from . import services
from .grpc_clients import get_materias_alumno, get_promedio_alumno, get_asistencia_alumno

DEV_BYPASS_AUTH = True
_perms = [AllowAny] if DEV_BYPASS_AUTH else []


def _serve(tipo, materia_id, formato, user_id):
    formato = formato.upper()
    fn = services.REGISTRO.get((tipo, formato))
    if not fn:
        return Response({"success": False, "message": f"Formato '{formato}' no soportado. Usa: PDF, XLS, XLSX"}, status=400)
    try:
        file_bytes, filename, mime = fn(materia_id)
    except Exception as e:
        return Response({"success": False, "message": f"Error al generar: {str(e)}"}, status=500)

    ReporteGenerado.objects.create(
        tipo=tipo, formato=formato, materia_id=str(materia_id),
        generado_por_user_id=str(user_id) if user_id else "dev",
        file_name=filename, size_bytes=len(file_bytes),
    )
    response = HttpResponse(file_bytes, content_type=mime)
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@api_view(["GET"])
@permission_classes(_perms)
def reporte_calificaciones(request, materia_id):
    return _serve("CALIFICACIONES", materia_id, request.query_params.get("formato", "pdf"), getattr(request.user, "id", None))


@api_view(["GET"])
@permission_classes(_perms)
def reporte_asistencias(request, materia_id):
    return _serve("ASISTENCIAS", materia_id, request.query_params.get("formato", "pdf"), getattr(request.user, "id", None))


@api_view(["GET"])
@permission_classes(_perms)
def historial_reportes(request):
    limit = int(request.query_params.get("limit", 20))
    qs = ReporteGenerado.objects.all()[:limit]
    return Response({"success": True, "data": ReporteGeneradoSerializer(qs, many=True).data})


@api_view(["GET"])
@permission_classes(_perms)
def estadisticas_docente(request, docente_id):
    from .grpc_clients import get_materia, get_estadisticas_materia, get_estadisticas_asistencia
    materia_ids = request.query_params.getlist("materia_id") or ["demo-001"]
    resultados = []
    for materia_id in materia_ids:
        materia = get_materia(materia_id)
        sc = get_estadisticas_materia(materia_id)
        sa = get_estadisticas_asistencia(materia_id)
        resultados.append({
            "materia_id": materia_id,
            "materia_nombre": materia.get("nombre", ""),
            "total_alumnos": sc.get("total_alumnos", 0),
            "aprobados": sc.get("aprobados", 0),
            "reprobados": sc.get("reprobados", 0),
            "promedio_grupal": sc.get("promedio_grupal", 0),
            "porcentaje_asistencia": sa.get("porcentaje_asistencia", 0),
        })
    return Response({"success": True, "docente_id": docente_id, "total_materias": len(resultados), "data": resultados})


@api_view(["GET"])
@permission_classes(_perms)
def estadisticas_alumno(request, alumno_id):
    materias = get_materias_alumno(alumno_id)
    resultados = []
    for materia in materias:
        materia_id = materia.get("id", "")
        promedio = get_promedio_alumno(materia_id, alumno_id)
        regs = get_asistencia_alumno(alumno_id, materia_id)
        total = len(regs)
        presentes = sum(1 for r in regs if r["estado"] == "PRESENTE")
        retardos  = sum(1 for r in regs if r["estado"] == "RETARDO")
        ausentes  = sum(1 for r in regs if r["estado"] == "AUSENTE")
        resultados.append({
            "materia_id": materia_id,
            "materia_nombre": materia.get("nombre", "Materia desconocida"),
            "promedio": promedio,
            "asistencia": {
                "total_sesiones": total,
                "presentes": presentes,
                "retardos": retardos,
                "ausentes": ausentes,
                "porcentaje": round((presentes + retardos) / total * 100, 1) if total else 0,
            },
        })
    return Response({"success": True, "alumno_id": alumno_id, "total_materias": len(resultados), "data": resultados})
