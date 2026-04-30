"""
Endpoints:
    POST /notificaciones/bienvenida
    POST /notificaciones/baja
    POST /notificaciones/cierre-materia
    POST /notificaciones/reset-password
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from . import services
from .serializers import (
    BienvenidaSerializer,
    BajaSerializer,
    CierreMateriaSerializer,
    ResetPasswordSerializer,
)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def bienvenida(request):
    s = BienvenidaSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    notif = services.enviar_bienvenida(**s.validated_data)
    return Response(
        {"success": notif.estado == "ENVIADO", "data": {"id": str(notif.id)}, "message": notif.error},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def baja(request):
    s = BajaSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    notif = services.enviar_baja(**s.validated_data)
    return Response(
        {"success": notif.estado == "ENVIADO", "data": {"id": str(notif.id)}, "message": notif.error},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cierre_materia(request):
    s = CierreMateriaSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    services.enviar_cierre_materia(**s.validated_data)
    return Response({"success": True, "message": ""}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reset_password(request):
    s = ResetPasswordSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    notif = services.enviar_reset_password(**s.validated_data)
    return Response(
        {"success": notif.estado == "ENVIADO", "data": {"id": str(notif.id)}, "message": notif.error},
        status=status.HTTP_201_CREATED,
    )
