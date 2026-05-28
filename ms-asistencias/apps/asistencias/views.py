"""
Endpoints:
    POST   /asistencias/registrar
    GET    /asistencias/<materia_id>/hoy
    GET    /asistencias/<materia_id>/historial
"""
import hashlib
from django.core.cache import cache
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from datetime import timedelta

from apps.sesiones.models import Sesion, EstadoSesion
from .models import Asistencia, EstadoAsistencia
from .serializers import RegistrarAsistenciaSerializer, AsistenciaSerializer


# ---------------------------------------------------------------------------
# Helper: cerrar sesión si ya expiró
# ---------------------------------------------------------------------------
def _verificar_expiracion(sesion: Sesion) -> bool:
    """
    Verifica si la sesión ya superó su duración.
    Si expiró, la cierra automáticamente y limpia Redis.
    Devuelve True si expiró, False si sigue activa.
    """
    ahora = timezone.now()
    fin_sesion = sesion.inicio + timedelta(minutes=sesion.duracion_minutos)

    if ahora >= fin_sesion:
        sesion.estado = EstadoSesion.CERRADA
        sesion.save(update_fields=["estado"])
        cache.delete(f"sesion:{sesion.id}:escaneados")
        cache.delete(f"sesion:{sesion.id}:token")
        return True

    return False


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def registrar_asistencia(request):
    """
    Registra asistencia cuando alumno escanea QR.

    Payload:
    {
        "sesion_id": "uuid",
        "qr_token": "token_uuid"
    }
    """
    serializer = RegistrarAsistenciaSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    sesion_id = serializer.validated_data["sesion_id"]
    qr_token = serializer.validated_data["qr_token"]

    # 1. Obtener sesión
    try:
        sesion = Sesion.objects.get(id=sesion_id, estado=EstadoSesion.ACTIVA)
    except Sesion.DoesNotExist:
        return Response(
            {"success": False, "message": "Sesión no existe o está cerrada"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 2. Verificar si ya expiró (cierre automático)
    if _verificar_expiracion(sesion):
        return Response(
            {"success": False, "message": "La sesión expiró y fue cerrada automáticamente"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 3. Validar token QR
    qr_token_hash = hashlib.sha256(qr_token.encode()).hexdigest()
    redis_key_token = f"sesion:{sesion.id}:token"
    stored_hash = cache.get(redis_key_token)

    if not stored_hash or stored_hash != qr_token_hash:
        return Response(
            {"success": False, "message": "Token QR inválido o expirado"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # 4. Calcular estado (PRESENTE o RETARDO)
    ahora = timezone.now()
    tiempo_transcurrido = (ahora - sesion.inicio).total_seconds() / 60

    if tiempo_transcurrido <= sesion.umbral_retardo_min:
        estado = EstadoAsistencia.PRESENTE
    else:
        estado = EstadoAsistencia.RETARDO

    # 5. Anti-duplicado via Redis
    redis_key_escaneados = f"sesion:{sesion.id}:escaneados"
    escaneados = cache.get(redis_key_escaneados) or set()
    alumno_id = str(request.user.id)

    if alumno_id in escaneados:
        return Response(
            {"success": False, "message": "Ya registraste asistencia en esta sesión"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 6. Registrar asistencia
    asistencia, created = Asistencia.objects.update_or_create(
        sesion=sesion,
        alumno_id=alumno_id,
        defaults={
            "materia_id":    sesion.materia_id,
            "estado":        estado,
            "qr_token_hash": qr_token_hash,
        },
    )

    # 7. Actualizar set en Redis
    escaneados.add(alumno_id)
    cache.set(
        redis_key_escaneados,
        escaneados,
        timeout=sesion.duracion_minutos * 60 + 60,
    )

    return Response(
        {
            "success": True,
            "data": AsistenciaSerializer(asistencia).data,
            "message": f"Asistencia registrada: {estado}",
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def asistencias_hoy(request, materia_id):
    """
    GET /asistencias/<materia_id>/hoy
    Retorna asistencias de una materia HOY.
    """
    hoy = timezone.now().date()

    asistencias = Asistencia.objects.filter(
        materia_id=materia_id,
        fecha__date=hoy,
    ).select_related("sesion")

    role = getattr(request.user, "role", None)
    if role == "DOCENTE":
        asistencias = asistencias.filter(sesion__docente_id=str(request.user.id))
    elif role == "ALUMNO":
        asistencias = asistencias.filter(alumno_id=str(request.user.id))

    return Response(
        {
            "success": True,
            "data": AsistenciaSerializer(asistencias, many=True).data,
            "count": asistencias.count(),
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def asistencias_historial(request, materia_id):
    """
    GET /asistencias/<materia_id>/historial
    Retorna historial de asistencias de una materia.

    Parámetros:
    - dias: últimos N días (default 30)
    """
    dias = request.query_params.get("dias", 30)
    try:
        dias = int(dias)
    except (ValueError, TypeError):
        dias = 30

    desde = timezone.now() - timedelta(days=dias)

    asistencias = Asistencia.objects.filter(
        materia_id=materia_id,
        fecha__gte=desde,
    ).select_related("sesion").order_by("-fecha")

    role = getattr(request.user, "role", None)
    if role == "DOCENTE":
        asistencias = asistencias.filter(sesion__docente_id=str(request.user.id))
    elif role == "ALUMNO":
        asistencias = asistencias.filter(alumno_id=str(request.user.id))

    return Response(
        {
            "success": True,
            "data": AsistenciaSerializer(asistencias, many=True).data,
            "count": asistencias.count(),
            "periodo": {"desde": desde.isoformat(), "dias": dias},
        }
    )