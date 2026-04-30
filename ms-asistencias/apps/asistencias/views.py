"""
Endpoints:
    POST /asistencias/registrar
    GET  /asistencias/<materia_id>/hoy
    GET  /asistencias/<materia_id>/historial
"""
import hashlib
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.sesiones.models import Sesion, EstadoSesion
from .models import Asistencia, EstadoAsistencia
from .serializers import RegistrarAsistenciaSerializer, AsistenciaSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def registrar_asistencia(request):
    """
    Procesa el QR escaneado por el docente.

    Validaciones:
        - sesión debe estar ACTIVA y no expirada
        - qr_token debe ser válido y no haber sido usado (anti-replay)
        - alumno debe estar inscrito en la materia (gRPC → MS-3)
    Clasificación:
        - PRESENTE si t < umbral_retardo_min
        - RETARDO  si umbral_retardo_min ≤ t < duracion_minutos
    """
    serializer = RegistrarAsistenciaSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # TODO:
    # 1. Obtener Sesion y validar estado/expiración
    # 2. Decrypt qr_token con Fernet/cryptography → obtener {alumno_id, sesion_id, ts}
    # 3. Validar que sesion_id del token == sesion_id del request (evita reuso entre sesiones)
    # 4. qr_hash = hashlib.sha256(qr_token).hexdigest()
    # 5. Comprobar en Redis: SADD sesion:{id}:escaneados qr_hash → si retorna 0 = ya usado
    # 6. Llamar gRPC a MS-3 IsAlumnoEnMateria(alumno_id, materia_id)
    # 7. Determinar estado según diferencia (now - sesion.inicio)
    # 8. Crear Asistencia
    return Response(
        {"success": True, "data": {}, "message": "TODO"},
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def asistencias_hoy(request, materia_id):
    """GET /asistencias/<materia_id>/hoy"""
    today = timezone.now().date()
    qs = Asistencia.objects.filter(materia_id=materia_id, fecha__date=today)
    return Response({"success": True, "data": AsistenciaSerializer(qs, many=True).data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def asistencias_historial(request, materia_id):
    """GET /asistencias/<materia_id>/historial – paginado."""
    qs = Asistencia.objects.filter(materia_id=materia_id).order_by("-fecha")
    return Response({"success": True, "data": AsistenciaSerializer(qs, many=True).data})
