"""
MS-6 Notificaciones – Worker RabbitMQ.

Este proceso se ejecuta como contenedor independiente (ver docker-compose.yml).
Escucha TODAS las colas de eventos AGM y delega en los services de Django.

Colas consumidas:
    agm.notificaciones.bienvenida  ← evento: alumno.registrado
    agm.notificaciones.baja        ← evento: alumno.baja
    agm.notificaciones.cierre      ← evento: materia.cerrada
    agm.notificaciones.reset       ← evento: auth.reset_password
    agm.notificaciones.reporte     ← evento: reporte.generado

Desacoplamiento real: si MS-3 (Alumnos) publica un evento y MS-6 está caído,
el mensaje queda persistido en RabbitMQ. Cuando MS-6 vuelve a levantar,
consume todos los mensajes pendientes sin perder ninguna notificación.
"""

import os
import sys
import django
import logging

# ── Configurar Django antes de importar modelos ─────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Ahora sí podemos importar módulos Django
from apps.notificaciones import services
from shared.rabbitmq.consumer import BaseConsumer

logger = logging.getLogger(__name__)

# ── Mapeo routing_key → handler ─────────────────────────────────────────────
HANDLERS = {
    "alumno.registrado":    "_handle_bienvenida",
    "alumno.baja":          "_handle_baja",
    "materia.cerrada":      "_handle_cierre_materia",
    "auth.reset_password":  "_handle_reset_password",
    "reporte.generado":     "_handle_reporte_generado",
}


class NotificacionesWorker(BaseConsumer):
    """
    Worker concreto de MS-6.
    Recibe cada evento y llama al service de Django correspondiente.
    """

    def handle(self, routing_key: str, payload: dict):
        handler_name = HANDLERS.get(routing_key)
        if not handler_name:
            logger.warning("[Worker] Routing key desconocida: %s", routing_key)
            return

        handler = getattr(self, handler_name, None)
        if handler:
            handler(payload)
        else:
            logger.error("[Worker] Handler '%s' no implementado", handler_name)

    # ── Handlers individuales ────────────────────────────────────────────────

    def _handle_bienvenida(self, payload: dict):
        """
        Evento: alumno.registrado
        Productor: MS-3 Alumnos
        Acción: enviar correo de bienvenida con clave única al alumno
        """
        try:
            services.enviar_bienvenida(
                alumno_email=payload.get("alumno_email", ""),
                alumno_nombre=payload.get("alumno_nombre", "Alumno"),
                materia_nombre=payload.get("materia_nombre", ""),
                clave_unica=payload.get("clave_unica", ""),
                alumno_id=payload.get("alumno_id"),
                materia_id=payload.get("materia_id"),
            )
            logger.info("[Worker] Bienvenida enviada a %s", payload.get("alumno_email"))
        except Exception as exc:
            logger.exception("[Worker] Error en _handle_bienvenida: %s", exc)
            raise  # Permite que el consumer haga nack del mensaje

    def _handle_baja(self, payload: dict):
        """
        Evento: alumno.baja
        Productor: MS-3 Alumnos
        Acción: notificar al docente que un alumno solicitó baja
        """
        try:
            services.enviar_baja(
                docente_email=payload.get("docente_email", ""),
                docente_nombre=payload.get("docente_nombre", "Docente"),
                alumno_nombre=payload.get("alumno_nombre", ""),
                materia_nombre=payload.get("materia_nombre", ""),
                motivo=payload.get("motivo", "solicitud voluntaria"),
                alumno_id=payload.get("alumno_id"),
                docente_id=payload.get("docente_id"),
                materia_id=payload.get("materia_id"),
            )
            logger.info("[Worker] Baja notificada al docente %s", payload.get("docente_email"))
        except Exception as exc:
            logger.exception("[Worker] Error en _handle_baja: %s", exc)
            raise

    def _handle_cierre_materia(self, payload: dict):
        """
        Evento: materia.cerrada
        Productor: MS-2 Periodos & Materias
        Acción: notificar masivamente a todos los alumnos de la materia
        """
        try:
            materia_nombre = payload.get("materia_nombre", "")
            periodo = payload.get("periodo", "")
            materia_id = payload.get("materia_id")
            alumnos = payload.get("alumnos", [])

            # Si el payload viene con lista vacía, consultamos MS-3 via gRPC
            if not alumnos and materia_id:
                alumnos = self._obtener_alumnos_grpc(materia_id)

            services.enviar_cierre_materia(
                materia_nombre=materia_nombre,
                alumnos=alumnos,
                periodo=periodo,
                materia_id=materia_id,
            )
            logger.info("[Worker] Cierre notificado a %d alumnos de '%s'",
                        len(alumnos), materia_nombre)
        except Exception as exc:
            logger.exception("[Worker] Error en _handle_cierre_materia: %s", exc)
            raise

    def _handle_reset_password(self, payload: dict):
        """
        Evento: auth.reset_password
        Productor: MS-1 Auth & Users
        Acción: enviar correo con enlace de recuperación de contraseña
        """
        try:
            services.enviar_reset_password(
                user_email=payload.get("user_email", ""),
                user_nombre=payload.get("user_nombre", "Usuario"),
                reset_link=payload.get("reset_link", ""),
                user_id=payload.get("user_id"),
            )
            logger.info("[Worker] Reset password enviado a %s", payload.get("user_email"))
        except Exception as exc:
            logger.exception("[Worker] Error en _handle_reset_password: %s", exc)
            raise

    def _handle_reporte_generado(self, payload: dict):
        """
        Evento: reporte.generado
        Productor: MS-7 Reportes & Estadísticas
        Acción: avisar al docente que su reporte está disponible para descarga
        """
        try:
            docente_email = payload.get("docente_email", "")
            if not docente_email and payload.get("docente_id"):
                docente_email = self._resolver_email_docente(payload["docente_id"])

            if docente_email:
                services.enviar_reporte_disponible(
                    docente_email=docente_email,
                    docente_nombre=payload.get("docente_nombre", "Docente"),
                    materia_nombre=payload.get("materia_nombre", ""),
                    tipo=payload.get("tipo", ""),
                    formato=payload.get("formato", ""),
                    file_name=payload.get("file_name", ""),
                    reporte_id=payload.get("reporte_id"),
                )
            logger.info("[Worker] Aviso de reporte enviado a %s", docente_email)
        except Exception as exc:
            logger.exception("[Worker] Error en _handle_reporte_generado: %s", exc)
            raise

    # ── Helpers gRPC (consultas síncronas desde el worker) ──────────────────

    def _obtener_alumnos_grpc(self, materia_id: str) -> list:
        """Consulta MS-3 via gRPC para obtener lista de alumnos."""
        try:
            import grpc
            from protos import alumnos_pb2, alumnos_pb2_grpc
            from django.conf import settings
            target = settings.GRPC_TARGETS.get("alumnos", "ms-alumnos:50053")
            with grpc.insecure_channel(target) as channel:
                stub = alumnos_pb2_grpc.AlumnosServiceStub(channel)
                resp = stub.GetAlumnosByMateria(
                    alumnos_pb2.GetAlumnosByMateriaRequest(materia_id=materia_id),
                    timeout=5,
                )
                return [
                    {
                        "email":  a.correo,
                        "nombre": a.nombre_completo,
                        "calificacion_final": None,
                    }
                    for a in resp.alumnos
                ]
        except Exception as exc:
            logger.warning("[Worker] No se pudieron obtener alumnos via gRPC: %s", exc)
            return []

    def _resolver_email_docente(self, docente_id: str) -> str:
        """Consulta MS-1 via gRPC para obtener el email del docente."""
        try:
            import grpc
            from protos import auth_pb2, auth_pb2_grpc
            from django.conf import settings
            target = settings.GRPC_TARGETS.get("auth", "ms-auth:50051")
            with grpc.insecure_channel(target) as channel:
                stub = auth_pb2_grpc.AuthServiceStub(channel)
                resp = stub.GetUserById(
                    auth_pb2.GetUserByIdRequest(user_id=docente_id),
                    timeout=5,
                )
                return resp.email
        except Exception as exc:
            logger.warning("[Worker] No se pudo resolver email docente: %s", exc)
            return ""


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(asctime)s %(name)s: %(message)s",
    )
    logger.info("Iniciando MS-6 Notificaciones Worker (RabbitMQ)...")
    worker = NotificacionesWorker()
    worker.run()
