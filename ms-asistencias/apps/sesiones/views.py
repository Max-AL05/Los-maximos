"""
Endpoints:
    POST   /sesiones/iniciar
    DELETE /sesiones/<id>/cerrar
"""
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
    # TODO:
    # 1. Verificar que no exista ya otra sesión ACTIVA para esa materia
    # 2. Crear Sesion con docente_id = request.user.id
    # 3. Inicializar set en Redis: "sesion:{id}:escaneados" con TTL = duracion+1min
    return Response(
        {"success": True, "data": {}, "message": "TODO"},
        status=status.HTTP_201_CREATED,
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def cerrar_sesion(request, sesion_id):
    """Cierra la sesión manualmente (también se cierra automáticamente al expirar)."""
    try:
        sesion = Sesion.objects.get(id=sesion_id)
    except Sesion.DoesNotExist:
        return Response({"success": False, "message": "No existe"}, status=404)
    sesion.estado = EstadoSesion.CERRADA
    sesion.save()
    # TODO: marcar como AUSENTE a los alumnos inscritos que no aparecen en asistencias
    return Response({"success": True, "data": SesionSerializer(sesion).data, "message": ""})
