"""
AGM – Módulo compartido: Consumer base para workers RabbitMQ.

Cada cola que MS-6 Notificaciones debe consumir queda declarada aquí.
El worker importa BaseConsumer y define su handler.

Colas declaradas:
    agm.notificaciones.bienvenida   ← routing key: alumno.registrado
    agm.notificaciones.baja         ← routing key: alumno.baja
    agm.notificaciones.cierre       ← routing key: materia.cerrada
    agm.notificaciones.reset        ← routing key: auth.reset_password
    agm.notificaciones.reporte      ← routing key: reporte.generado
"""

import json
import logging
import os
import time

import pika
from pika.exceptions import AMQPConnectionError

logger = logging.getLogger(__name__)

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "agm_user")
RABBITMQ_PASS = os.environ.get("RABBITMQ_PASS", "agm_password")
RABBITMQ_VHOST = os.environ.get("RABBITMQ_VHOST", "/")

EXCHANGE_NAME = "agm.events"

# Definición de colas: (nombre_cola, routing_key)
QUEUE_BINDINGS = [
    ("agm.notificaciones.bienvenida", "alumno.registrado"),
    ("agm.notificaciones.baja",       "alumno.baja"),
    ("agm.notificaciones.cierre",     "materia.cerrada"),
    ("agm.notificaciones.reset",      "auth.reset_password"),
    ("agm.notificaciones.reporte",    "reporte.generado"),
]


def _get_connection() -> pika.BlockingConnection:
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    params = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host=RABBITMQ_VHOST,
        credentials=credentials,
        heartbeat=60,
        blocked_connection_timeout=300,
    )
    return pika.BlockingConnection(params)


class BaseConsumer:
    """
    Consumer base con reconexión automática.

    Subclasificar y definir `handle(queue_name, payload)`.
    """

    def setup_queues(self, channel):
        """Declara exchange y todas las colas con sus bindings."""
        channel.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type="topic",
            durable=True,
        )
        for queue_name, routing_key in QUEUE_BINDINGS:
            channel.queue_declare(queue=queue_name, durable=True)
            channel.queue_bind(
                queue=queue_name,
                exchange=EXCHANGE_NAME,
                routing_key=routing_key,
            )
            logger.info("[RabbitMQ] Cola lista: %s → %s", routing_key, queue_name)

    def handle(self, queue_name: str, payload: dict):
        """Override en el subclase para procesar el mensaje."""
        raise NotImplementedError

    def _callback(self, ch, method, properties, body):
        queue_name = method.routing_key  # usamos la routing key para identificar
        try:
            payload = json.loads(body.decode("utf-8"))
            logger.info("[RabbitMQ] Mensaje recibido: %s", method.routing_key)
            # Pasamos el nombre de la cola para que el handler sepa qué hacer
            self.handle(method.routing_key, payload)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as exc:
            logger.exception("[RabbitMQ] Error procesando '%s': %s", method.routing_key, exc)
            # Nack sin requeue para no entrar en bucle infinito con mensajes dañados
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def run(self):
        """Inicia el consumer con reconexión automática."""
        while True:
            try:
                connection = _get_connection()
                channel = connection.channel()
                channel.basic_qos(prefetch_count=1)
                self.setup_queues(channel)

                # Registrar el mismo callback para todas las colas
                for queue_name, _ in QUEUE_BINDINGS:
                    channel.basic_consume(
                        queue=queue_name,
                        on_message_callback=self._callback,
                    )

                logger.info("[RabbitMQ] Worker iniciado. Esperando mensajes...")
                channel.start_consuming()

            except AMQPConnectionError as exc:
                logger.warning("[RabbitMQ] Conexión perdida, reconectando en 5s: %s", exc)
                time.sleep(5)
            except KeyboardInterrupt:
                logger.info("[RabbitMQ] Worker detenido manualmente.")
                break
            except Exception as exc:
                logger.exception("[RabbitMQ] Error inesperado, reconectando en 5s: %s", exc)
                time.sleep(5)
