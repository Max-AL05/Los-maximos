"""
AGM – Módulo compartido: Publisher de eventos hacia RabbitMQ.

Uso desde cualquier microservicio productor:

    from shared.rabbitmq.publisher import publish_event
    publish_event("alumno.registrado", {"alumno_id": "...", "correo": "..."})

Cada microservicio publica en el exchange 'agm.events' (tipo topic).
MS-6 Notificaciones consume las colas que le corresponden.
"""

import json
import logging
import os

import pika
from pika.exceptions import AMQPConnectionError

logger = logging.getLogger(__name__)

# ── Configuración desde variables de entorno ────────────────────────────────
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "agm_user")
RABBITMQ_PASS = os.environ.get("RABBITMQ_PASS", "agm_password")
RABBITMQ_VHOST = os.environ.get("RABBITMQ_VHOST", "/")

# Exchange único compartido por todos los MS (tipo topic)
EXCHANGE_NAME = "agm.events"


def _get_connection() -> pika.BlockingConnection:
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    params = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host=RABBITMQ_VHOST,
        credentials=credentials,
        connection_attempts=3,
        retry_delay=2,
        socket_timeout=5,
    )
    return pika.BlockingConnection(params)


def publish_event(routing_key: str, payload: dict) -> bool:
    """
    Publica un evento en el exchange 'agm.events'.

    Args:
        routing_key: clave de enrutamiento, ej. "alumno.registrado"
        payload:     dict con los datos del evento (se serializa a JSON)

    Returns:
        True si el mensaje fue confirmado (publisher confirms), False si falló.

    Routing keys usadas en AGM:
        alumno.registrado       → MS-3 → MS-6
        alumno.baja             → MS-3 → MS-6
        materia.cerrada         → MS-2 → MS-6
        auth.reset_password     → MS-1 → MS-6
        reporte.generado        → MS-7 → MS-6
    """
    try:
        connection = _get_connection()
        channel = connection.channel()

        # Declarar exchange idempotente (durable = sobrevive reinicios)
        channel.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type="topic",
            durable=True,
        )

        # Habilitar confirmaciones del broker (publisher confirms)
        channel.confirm_delivery()

        body = json.dumps(payload, ensure_ascii=False, default=str)

        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=routing_key,
            body=body.encode("utf-8"),
            properties=pika.BasicProperties(
                delivery_mode=2,          # persistente (sobrevive a reinicio del broker)
                content_type="application/json",
            ),
        )

        connection.close()
        logger.info("[RabbitMQ] Evento publicado: %s", routing_key)
        return True

    except AMQPConnectionError as exc:
        logger.error("[RabbitMQ] No se pudo conectar al broker: %s", exc)
        return False
    except Exception as exc:
        logger.error("[RabbitMQ] Error publicando '%s': %s", routing_key, exc)
        return False
