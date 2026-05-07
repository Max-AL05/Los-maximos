from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import ReporteGenerado
from .serializers import ReporteGeneradoSerializer
from . import services

# Cambia a False antes de la entrega final
DEV_BYPASS_AUTH = True


def _serve(tipo, materia_id, formato, user_id):
    formato = formato.upper()
    fn = services.REGISTRO.get((tipo, formato))
    if not fn:
        return Response({"success": False, "message": "Formato no soportado"}, status=400)

    file_bytes, filename, mime = fn(materia_id)

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


_perms = [AllowAny] if DEV_BYPASS_AUTH else [IsAuthenticated]


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
    return Response({"success": True, "data": ReporteGeneradoSerializer(qs, many=True).data})