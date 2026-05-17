"""
Endpoints REST para sesiones de asistencia QR.

    POST   /sesiones/iniciar        → Docente inicia una sesión de 10 min
    DELETE /sesiones/<id>/cerrar    → Docente cierra la sesión manualmente
"""
import json
import hashlib

from django.conf import settings
from django.core.cache import cache
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
    """
    Inicia una nueva sesión de pase de lista para una materia.

    Solo puede existir UNA sesión ACTIVA por materia a la vez.
    Al crear la sesión, inicializa en Redis el set de QRs ya escaneados
    con un TTL = duracion_minutos + 1 min (margen de seguridad).

    Body JSON:
        materia_id        (uuid, requerido)
        duracion_minutos  (int,  default=10)
        umbral_retardo_min (int, default=5)

    Respuesta exitosa:
        {"success": true, "data": {sesion...}, "message": "Sesión iniciada"}
    """
    serializer = IniciarSesionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    materia_id = str(serializer.validated_data["materia_id"])
    duracion = serializer.validated_data.get("duracion_minutos", 10)
    umbral = serializer.validated_data.get("umbral_retardo_min", 5)

    # 1. Verificar que no exista ya una sesión ACTIVA para esta materia
    sesion_activa = Sesion.objects.filter(
        materia_id=materia_id,
        estado=EstadoSesion.ACTIVA
    ).first()

    if sesion_activa:
        # Verificar si ya expiró (Django no la cierra automáticamente)
        if timezone.now() > sesion_activa.fin:
            # Expiró → cerrarla automáticamente
            sesion_activa.estado = EstadoSesion.CERRADA
            sesion_activa.save(update_fields=["estado"])
        else:
            return Response(
                {
                    "success": False,
                    "data": SesionSerializer(sesion_activa).data,
                    "message": "Ya existe una sesión activa para esta materia. Ciérrala primero.",
                },
                status=status.HTTP_409_CONFLICT,
            )

    # 2. Crear la nueva sesión en base de datos
    sesion = Sesion.objects.create(
        materia_id=materia_id,
        docente_id=str(request.user.id),   # ID del docente autenticado
        duracion_minutos=duracion,
        umbral_retardo_min=umbral,
        estado=EstadoSesion.ACTIVA,
    )

    # 3. Inicializar set en Redis para el anti-replay de tokens QR.
    #    Clave: "sesion:<uuid>:escaneados"
    #    TTL: duracion en segundos + 60 segundos de margen
    redis_key = f"sesion:{sesion.id}:escaneados"
    ttl_segundos = (duracion * 60) + 60

    # Guardamos un marcador vacío (el set se pobla al registrar asistencias)
    cache.set(redis_key, json.dumps([]), timeout=ttl_segundos)

    return Response(
        {
            "success": True,
            "data": SesionSerializer(sesion).data,
            "message": f"Sesión iniciada. Durará {duracion} minutos.",
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def cerrar_sesion(request, sesion_id):
    """
    Cierra una sesión de pase de lista manualmente.

    Al cerrar, marca como AUSENTE a todos los alumnos inscritos
    en la materia que NO tengan registro de asistencia en esta sesión.
    (Requiere llamada gRPC a MS-3 para obtener la lista de alumnos.)

    Respuesta exitosa:
        {"success": true, "data": {sesion...}, "message": "Sesión cerrada"}
    """
    # 1. Buscar la sesión
    try:
        sesion = Sesion.objects.get(id=sesion_id)
    except Sesion.DoesNotExist:
        return Response(
            {"success": False, "data": {}, "message": "Sesión no encontrada."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # 2. Validar que la sesión no esté ya cerrada
    if sesion.estado == EstadoSesion.CERRADA:
        return Response(
            {
                "success": False,
                "data": SesionSerializer(sesion).data,
                "message": "La sesión ya estaba cerrada.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 3. Cerrar la sesión
    sesion.estado = EstadoSesion.CERRADA
    sesion.save(update_fields=["estado"])

    # 4. Marcar como AUSENTE a los alumnos que no escanearon QR
    #    Se obtiene la lista de inscritos via gRPC MS-3 y se compara
    #    con los que ya tienen registro en Asistencia para esta sesión.
    try:
        import grpc
        from django.conf import settings as dj_settings
        # Importar stubs generados (deben existir en ms-asistencias/protos/)
        from protos import alumnos_pb2, alumnos_pb2_grpc
        from apps.asistencias.models import Asistencia, EstadoAsistencia

        grpc_target = dj_settings.GRPC_TARGETS.get("alumnos", "localhost:50053")
        canal = grpc.insecure_channel(grpc_target)
        stub = alumnos_pb2_grpc.AlumnosServiceStub(canal)

        # Obtener alumnos inscritos en la materia desde MS-3
        respuesta = stub.GetAlumnosByMateria(
            alumnos_pb2.GetAlumnosByMateriaRequest(materia_id=str(sesion.materia_id)),
            timeout=5,
        )

        # IDs de alumnos que SÍ registraron asistencia en esta sesión
        ids_presentes = set(
            Asistencia.objects.filter(sesion=sesion)
            .values_list("alumno_id", flat=True)
        )

        # Crear registros AUSENTE para los que no escanearon
        ausentes_creados = []
        for alumno_info in respuesta.alumnos:
            alumno_id = alumno_info.alumno_id
            if alumno_id not in ids_presentes and alumno_info.activo_en_materia:
                # Evitar duplicados (por si se llama cerrar dos veces)
                _, creada = Asistencia.objects.get_or_create(
                    sesion=sesion,
                    alumno_id=alumno_id,
                    defaults={
                        "materia_id": str(sesion.materia_id),
                        "estado": EstadoAsistencia.AUSENTE,
                        "qr_token_hash": hashlib.sha256(
                            f"ausente_{sesion.id}_{alumno_id}".encode()
                        ).hexdigest(),
                    },
                )
                if creada:
                    ausentes_creados.append(alumno_id)

        canal.close()
        mensaje = (
            f"Sesión cerrada. "
            f"{len(ids_presentes)} presentes/retardos, "
            f"{len(ausentes_creados)} marcados como ausentes."
        )

    except Exception as exc:
        # Si falla gRPC, cerramos igual pero avisamos
        mensaje = (
            f"Sesión cerrada. "
            f"Advertencia: no se pudo registrar ausentes automáticamente ({exc})."
        )

    return Response(
        {
            "success": True,
            "data": SesionSerializer(sesion).data,
            "message": mensaje,
        },
        status=status.HTTP_200_OK,
    )