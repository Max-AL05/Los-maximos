
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from . import services
from .models import Notificacion
from .serializers import (
    BienvenidaSerializer,
    BajaSerializer,
    CierreMateriaSerializer,
    ResetPasswordSerializer,
    NotificacionSerializer,
)


# ============================================================================
# POST /notificaciones/bienvenida
# ============================================================================
@extend_schema(
    request=BienvenidaSerializer,
    responses={201: NotificacionSerializer},
    summary="Envía email de bienvenida con clave única",
    tags=["Notificaciones"],
)
@api_view(["POST"])
def bienvenida(request):
    serializer = BienvenidaSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    notif = services.enviar_bienvenida(**serializer.validated_data)
    return Response(NotificacionSerializer(notif).data, status=status.HTTP_201_CREATED)


# ============================================================================
# POST /notificaciones/baja
# ============================================================================
@extend_schema(
    request=BajaSerializer,
    responses={201: NotificacionSerializer},
    summary="Avisa al docente que un alumno se dio de baja",
    tags=["Notificaciones"],
)
@api_view(["POST"])
def baja(request):
    serializer = BajaSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    notif = services.enviar_baja(**serializer.validated_data)
    return Response(NotificacionSerializer(notif).data, status=status.HTTP_201_CREATED)


# ============================================================================
# POST /notificaciones/cierre-materia
# ============================================================================
@extend_schema(
    request=CierreMateriaSerializer,
    responses={201: NotificacionSerializer(many=True)},
    summary="Envío masivo a todos los alumnos al cerrar una materia",
    tags=["Notificaciones"],
)
@api_view(["POST"])
def cierre_materia(request):
    serializer = CierreMateriaSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    notifs = services.enviar_cierre_materia(**serializer.validated_data)
    return Response(
        NotificacionSerializer(notifs, many=True).data,
        status=status.HTTP_201_CREATED,
    )


# ============================================================================
# POST /notificaciones/reset-password
# ============================================================================
@extend_schema(
    request=ResetPasswordSerializer,
    responses={201: NotificacionSerializer},
    summary="Envía link de recuperación de contraseña",
    tags=["Notificaciones"],
)
@api_view(["POST"])
def reset_password(request):
    serializer = ResetPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    notif = services.enviar_reset_password(**serializer.validated_data)
    return Response(NotificacionSerializer(notif).data, status=status.HTTP_201_CREATED)


# ============================================================================
# GET /notificaciones/  (lista con paginación implícita y filtros)
# GET /notificaciones/<uuid:pk>/
# ============================================================================
class NotificacionListView(ListAPIView):
    """Lista todas las notificaciones, con filtros opcionales por tipo/estado/email."""
    serializer_class = NotificacionSerializer

    def get_queryset(self):
        qs = Notificacion.objects.all()
        tipo = self.request.query_params.get("tipo")
        estado = self.request.query_params.get("estado")
        email = self.request.query_params.get("email")
        if tipo:
            qs = qs.filter(tipo=tipo)
        if estado:
            qs = qs.filter(estado=estado)
        if email:
            qs = qs.filter(destinatario_email__icontains=email)
        return qs


class NotificacionDetailView(RetrieveAPIView):
    """Detalle de una notificación por UUID."""
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer
    lookup_field = "id"
