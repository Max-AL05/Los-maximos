"""
Endpoints REST para registrar y consultar asistencias.

    POST /asistencias/registrar              → Docente registra QR escaneado
    GET  /asistencias/<materia_id>/hoy       → Lista asistencias del día
    GET  /asistencias/<materia_id>/historial → Historial paginado por materia
"""
import hashlib
import json

from cryptography.fernet import Fernet, InvalidToken

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.sesiones.models import Sesion, EstadoSesion
from .models import Asistencia, EstadoAsistencia
from .serializers import RegistrarAsistenciaSerializer, AsistenciaSerializer


# ---------------------------------------------------------------------------
# Helper: obtener instancia Fernet con la clave del entorno
# ---------------------------------------------------------------------------
def _get_fernet():
    """Retorna una instancia Fernet con la clave configurada en QR_FERNET_KEY."""
    clave = settings.QR_FERNET_KEY
    if not clave:
        raise ValueError("QR_FERNET_KEY no está configurada en las variables de entorno.")
    return Fernet(clave.encode() if isinstance(clave, str) else clave)


# ---------------------------------------------------------------------------
# POST /asistencias/registrar
# ---------------------------------------------------------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def registrar_asistencia(request):
    """
    Registra la asistencia de un alumno a partir del contenido del QR escaneado.

    Flujo completo:
        1. Validar body con serializer
        2. Obtener la sesión y verificar que esté ACTIVA y no expirada
        3. Descifrar qr_token con Fernet → payload {alumno_id, sesion_id, ts}
        4. Verificar que sesion_id del token == sesion_id del request (anti-reuso cruzado)
        5. Calcular hash del token y verificar anti-replay en Redis
        6. Llamar gRPC a MS-3 → IsAlumnoEnMateria(alumno_id, materia_id)
        7. Determinar estado: PRESENTE o RETARDO según marca de tiempo
        8. Persistir registro en base de datos
        9. Responder con el registro creado

    Body JSON:
        sesion_id   (uuid, requerido)   → ID de la sesión activa
        qr_token    (str, requerido)    → Contenido del QR cifrado con Fernet

    Respuesta exitosa (201):
        {"success": true, "data": {asistencia...}, "message": "Asistencia registrada"}

    Errores posibles:
        400 → QR inválido, sesión expirada, alumno no inscrito
        409 → QR ya fue usado (anti-replay) o alumno ya registrado en esta sesión
        404 → Sesión no encontrada
    """
    serializer = RegistrarAsistenciaSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    sesion_id = str(serializer.validated_data["sesion_id"])
    qr_token = serializer.validated_data["qr_token"]

    # ------------------------------------------------------------------
    # PASO 1: Obtener la sesión y validar estado
    # ------------------------------------------------------------------
    try:
        sesion = Sesion.objects.get(id=sesion_id)
    except Sesion.DoesNotExist:
        return Response(
            {"success": False, "data": {}, "message": "Sesión no encontrada."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # La sesión debe estar ACTIVA
    if sesion.estado != EstadoSesion.ACTIVA:
        return Response(
            {"success": False, "data": {}, "message": "La sesión no está activa."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Verificar que la sesión no haya expirado por tiempo
    ahora = timezone.now()
    if ahora > sesion.fin:
        # Cerrar automáticamente la sesión expirada
        sesion.estado = EstadoSesion.CERRADA
        sesion.save(update_fields=["estado"])
        return Response(
            {"success": False, "data": {}, "message": "La sesión ya expiró."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ------------------------------------------------------------------
    # PASO 2: Descifrar el token QR con Fernet
    # ------------------------------------------------------------------
    try:
        fernet = _get_fernet()
        # El token puede llegar como string o bytes
        token_bytes = qr_token.encode() if isinstance(qr_token, str) else qr_token
        payload_json = fernet.decrypt(token_bytes).decode("utf-8")
        payload = json.loads(payload_json)
    except InvalidToken:
        return Response(
            {"success": False, "data": {}, "message": "Token QR inválido o mal formado."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as exc:
        return Response(
            {"success": False, "data": {}, "message": f"Error al descifrar el QR: {exc}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Extraer campos del payload descifrado
    alumno_id = payload.get("alumno_id")
    sesion_id_token = payload.get("sesion_id")
    ts = payload.get("ts")   # timestamp de cuando se generó el QR (segundos epoch)

    if not alumno_id or not sesion_id_token or ts is None:
        return Response(
            {"success": False, "data": {}, "message": "Payload del QR incompleto."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ------------------------------------------------------------------
    # PASO 3: Validar que el token pertenece a ESTA sesión (anti-reuso cruzado)
    # ------------------------------------------------------------------
    if str(sesion_id_token) != str(sesion.id):
        return Response(
            {
                "success": False,
                "data": {},
                "message": "El token QR pertenece a una sesión diferente.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ------------------------------------------------------------------
    # PASO 4: Anti-replay en Redis
    #    Calculamos SHA-256 del token original y lo guardamos en el set
    #    de la sesión. Si ya existía → token repetido → rechazar.
    # ------------------------------------------------------------------
    qr_hash = hashlib.sha256(token_bytes).hexdigest()
    redis_key = f"sesion:{sesion.id}:escaneados"

    # Leer el set actual desde Redis
    escaneados_raw = cache.get(redis_key)
    if escaneados_raw is None:
        # La clave expiró en Redis (sesión muy larga o reinicio de Redis)
        escaneados = []
    else:
        escaneados = json.loads(escaneados_raw)

    if qr_hash in escaneados:
        return Response(
            {
                "success": False,
                "data": {},
                "message": "Este token QR ya fue utilizado (anti-replay).",
            },
            status=status.HTTP_409_CONFLICT,
        )

    # Agregar el hash al set y volver a guardar en Redis
    escaneados.append(qr_hash)
    ttl_restante = int((sesion.fin - ahora).total_seconds()) + 60
    cache.set(redis_key, json.dumps(escaneados), timeout=max(ttl_restante, 1))

    # ------------------------------------------------------------------
    # PASO 5: Verificar inscripción del alumno vía gRPC → MS-3
    # ------------------------------------------------------------------
    materia_id = str(sesion.materia_id)
    try:
        import grpc
        from protos import alumnos_pb2, alumnos_pb2_grpc

        grpc_target = settings.GRPC_TARGETS.get("alumnos", "localhost:50053")
        canal = grpc.insecure_channel(grpc_target)
        stub = alumnos_pb2_grpc.AlumnosServiceStub(canal)

        respuesta_grpc = stub.IsAlumnoEnMateria(
            alumnos_pb2.IsAlumnoEnMateriaRequest(
                alumno_id=str(alumno_id),
                materia_id=materia_id,
            ),
            timeout=5,
        )
        canal.close()

        if not respuesta_grpc.inscrito:
            return Response(
                {
                    "success": False,
                    "data": {},
                    "message": "El alumno no está inscrito en esta materia.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if respuesta_grpc.dado_de_baja:
            return Response(
                {
                    "success": False,
                    "data": {},
                    "message": "El alumno está dado de baja en esta materia.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    except Exception as exc:
        # Si gRPC falla, registramos igualmente pero con advertencia en logs
        # En producción podría configurarse como fallo duro según política del equipo
        import logging
        logging.getLogger(__name__).warning(
            "gRPC MS-3 falló al verificar inscripción: %s. Se registrará de todas formas.", exc
        )

    # ------------------------------------------------------------------
    # PASO 6: Determinar estado (PRESENTE o RETARDO)
    # ------------------------------------------------------------------
    # Tiempo transcurrido desde que inició la sesión hasta que se escanea
    segundos_transcurridos = (ahora - sesion.inicio).total_seconds()
    minutos_transcurridos = segundos_transcurridos / 60.0

    if minutos_transcurridos < sesion.umbral_retardo_min:
        estado_asistencia = EstadoAsistencia.PRESENTE
    else:
        estado_asistencia = EstadoAsistencia.RETARDO

    # ------------------------------------------------------------------
    # PASO 7: Persistir la asistencia en base de datos
    # ------------------------------------------------------------------
    try:
        asistencia, creada = Asistencia.objects.get_or_create(
            sesion=sesion,
            alumno_id=str(alumno_id),
            defaults={
                "materia_id": materia_id,
                "estado": estado_asistencia,
                "qr_token_hash": qr_hash,
            },
        )
    except Exception as exc:
        return Response(
            {"success": False, "data": {}, "message": f"Error al guardar asistencia: {exc}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if not creada:
        return Response(
            {
                "success": False,
                "data": AsistenciaSerializer(asistencia).data,
                "message": "Este alumno ya tiene asistencia registrada en esta sesión.",
            },
            status=status.HTTP_409_CONFLICT,
        )

    return Response(
        {
            "success": True,
            "data": AsistenciaSerializer(asistencia).data,
            "message": f"Asistencia registrada como {estado_asistencia}.",
        },
        status=status.HTTP_201_CREATED,
    )


# ---------------------------------------------------------------------------
# GET /asistencias/<materia_id>/hoy
# ---------------------------------------------------------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def asistencias_hoy(request, materia_id):
    """
    Retorna todas las asistencias de la materia correspondientes a la fecha actual.

    URL param: materia_id (uuid)

    Respuesta:
        {"success": true, "data": [...asistencias...], "message": ""}
    """
    today = timezone.now().date()

    # Filtrar asistencias de hoy para esta materia
    qs = Asistencia.objects.filter(
        materia_id=str(materia_id),
        fecha__date=today,
    ).order_by("-fecha")

    return Response(
        {
            "success": True,
            "data": AsistenciaSerializer(qs, many=True).data,
            "message": f"{qs.count()} asistencia(s) registradas hoy.",
        },
        status=status.HTTP_200_OK,
    )


# ---------------------------------------------------------------------------
# GET /asistencias/<materia_id>/historial
# ---------------------------------------------------------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def asistencias_historial(request, materia_id):
    """
    Retorna el historial completo de asistencias de la materia, ordenado por fecha desc.
    Soporta filtrado opcional por alumno_id y estado via query params.

    Query params opcionales:
        alumno_id → filtra por alumno específico
        estado    → PRESENTE | RETARDO | AUSENTE
        fecha     → filtra por fecha exacta (YYYY-MM-DD)

    Respuesta:
        {"success": true, "data": [...asistencias...], "message": ""}
    """
    qs = Asistencia.objects.filter(materia_id=str(materia_id))

    # Filtros opcionales por query params
    alumno_id = request.query_params.get("alumno_id")
    estado = request.query_params.get("estado")
    fecha = request.query_params.get("fecha")

    if alumno_id:
        qs = qs.filter(alumno_id=alumno_id)

    if estado and estado in [e.value for e in EstadoAsistencia]:
        qs = qs.filter(estado=estado)

    if fecha:
        qs = qs.filter(fecha__date=fecha)

    qs = qs.order_by("-fecha")

    return Response(
        {
            "success": True,
            "data": AsistenciaSerializer(qs, many=True).data,
            "message": f"{qs.count()} registro(s) en el historial.",
        },
        status=status.HTTP_200_OK,
    )