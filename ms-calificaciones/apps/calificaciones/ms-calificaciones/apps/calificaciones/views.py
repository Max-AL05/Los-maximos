"""
Endpoints REST de calificaciones.

La autenticación está delegada a:
    - El middleware JWT (apps.calificaciones.middleware.JWTAuthMiddleware)
      que valida el token con MS-1 antes de llegar a la vista.
    - DRF DEFAULT_PERMISSION_CLASSES en settings.

NO sobrescribimos `permission_classes` aquí: si lo hacemos a `AllowAny`
volvemos a abrir el endpoint a internet aunque el middleware esté activo.
"""
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .models import Actividad, Calificacion
from .serializers import (
    ActividadSerializer,
    CalificacionSerializer,
    ConcentradoAlumnoSerializer,
    ImportarCalificacionesSerializer,
)
from .services import CalificacionesService


class ActividadViewSet(viewsets.ModelViewSet):
    """CRUD de actividades."""
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer


class CalificacionViewSet(viewsets.ModelViewSet):
    """CRUD de calificaciones individuales."""
    queryset = Calificacion.objects.all()
    serializer_class = CalificacionSerializer


@api_view(["POST"])
@parser_classes([MultiPartParser])
def importar_calificaciones(request):
    """POST /calificaciones/importar/ — importación masiva Excel/CSV."""
    serializer = ImportarCalificacionesSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    actividad_id = serializer.validated_data["actividad_id"]
    archivo = request.FILES["archivo_excel"]

    exito, resultado = CalificacionesService.procesar_archivo_masivo(actividad_id, archivo)
    if exito:
        return Response(
            {
                "success": True,
                "data": {"importadas": resultado},
                "message": "Importación masiva finalizada.",
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(
        {"success": False, "message": f"Error al procesar el archivo: {resultado}"},
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["GET"])
def concentrado(request, materia_id):
    """
    GET /concentrado/<materia_id>/

    Retorna el listado de inscritos activos con su promedio ponderado
    real, redondeado y estatus (APROBADO | EN_RIESGO | REPROBADO).
    """
    datos = CalificacionesService.obtener_concentrado_detallado(materia_id)

    if not datos:
        return Response(
            {
                "success": False,
                "message": (
                    "No se pudo generar el concentrado. Verifica que la materia "
                    "tenga rúbrica configurada y alumnos inscritos activos."
                ),
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = ConcentradoAlumnoSerializer(datos, many=True)
    return Response(
        {
            "success": True,
            "data": serializer.data,
            "message": "Concentrado generado correctamente.",
        },
        status=status.HTTP_200_OK,
    )