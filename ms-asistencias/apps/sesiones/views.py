"""
Endpoints:
    POST   /sesiones/iniciar
    DELETE /sesiones/<id>/cerrar
    GET    /sesiones/<id>/qr         (genera QR en PNG)
"""
import hashlib
import uuid as uuid_lib
from datetime import datetime, timedelta
from io import BytesIO

import qrcode
from django.core.cache import cache
from django.http import FileResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Sesion, EstadoSesion
from .serializers import IniciarSesionSerializer, SesionSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def iniciar_sesion(request):
    """Inicia una sesión de 10 min para una materia."""
    serializer = IniciarSesionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    materia_id = serializer.validated_data["materia_id"]
    duracion = serializer.validated_data.get("duracion_minutos", 10)
    umbral = serializer.validated_data.get("umbral_retardo_min", 5)

    # 1. Verificar que no exista sesión ACTIVA para esa materia
    sesion_activa = Sesion.objects.filter(
        materia_id=materia_id, estado=EstadoSesion.ACTIVA
    ).first()

    if sesion_activa:
        return Response(
            {
                "success": False,
                "message": f"Ya existe sesión activa para esta materia (ID: {sesion_activa.id})",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 2. Crear Sesion
    sesion = Sesion.objects.create(
        materia_id=materia_id,
        docente_id=str(request.user.id),
        duracion_minutos=duracion,
        umbral_retardo_min=umbral,
        estado=EstadoSesion.ACTIVA,
    )

    # 3. Inicializar en Redis set de escaneados
    # Clave: "sesion:{id}:escaneados" → set de matrículas que escanearon
    redis_key = f"sesion:{sesion.id}:escaneados"
    cache.set(redis_key, set(), timeout=duracion * 60 + 60)  # +1min buffer

    # 4. Generar token QR
    qr_token = str(uuid_lib.uuid4())
    qr_token_hash = hashlib.sha256(qr_token.encode()).hexdigest()

    # Guardar token en Redis para validación posterior
    redis_key_token = f"sesion:{sesion.id}:token"
    cache.set(redis_key_token, qr_token_hash, timeout=duracion * 60 + 60)

    return Response(
        {
            "success": True,
            "data": {
                **SesionSerializer(sesion).data,
                "qr_token": qr_token,  # Cliente guarda esto
            },
            "message": f"Sesión iniciada: {sesion.id}",
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def generar_qr(request, sesion_id):
    """
    Genera PNG de código QR con payload:
    {
        "sesion_id": "uuid",
        "token": "token_unico"
    }
    """
    try:
        sesion = Sesion.objects.get(id=sesion_id, estado=EstadoSesion.ACTIVA)
    except Sesion.DoesNotExist:
        return Response(
            {"success": False, "message": "Sesión no existe o está cerrada"},
            status=404,
        )

    # Obtener token desde Redis
    redis_key_token = f"sesion:{sesion.id}:token"
    qr_token_hash = cache.get(redis_key_token)

    if not qr_token_hash:
        return Response(
            {"success": False, "message": "Token expirado o sesión cerrada"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Generar nuevo token para cada QR (anti-replay)
    qr_token = str(uuid_lib.uuid4())
    new_hash = hashlib.sha256(qr_token.encode()).hexdigest()
    cache.set(redis_key_token, new_hash, timeout=sesion.duracion_minutos * 60 + 60)

    # Payload QR
    qr_payload = f"{sesion.id}|{qr_token}"

    # Generar PNG
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_payload)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img_io = BytesIO()
    img.save(img_io, "PNG")
    img_io.seek(0)

    return FileResponse(img_io, content_type="image/png")


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def cerrar_sesion(request, sesion_id):
    """Cierra la sesión manualmente (también se cierra automáticamente al expirar)."""
    try:
        sesion = Sesion.objects.get(id=sesion_id)
    except Sesion.DoesNotExist:
        return Response({"success": False, "message": "No existe"}, status=404)

    if sesion.estado == EstadoSesion.CERRADA:
        return Response(
            {"success": False, "message": "Sesión ya está cerrada"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    sesion.estado = EstadoSesion.CERRADA
    sesion.save()

    # Limpiar Redis
    redis_key = f"sesion:{sesion.id}:escaneados"
    redis_key_token = f"sesion:{sesion.id}:token"
    cache.delete(redis_key)
    cache.delete(redis_key_token)

    # TODO: marcar como AUSENTE a los alumnos inscritos que no aparecen en asistencias

    return Response(
        {
            "success": True,
            "data": SesionSerializer(sesion).data,
            "message": "Sesión cerrada",
        }
    )