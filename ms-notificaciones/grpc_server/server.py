"""
Servidor gRPC de ms-notificaciones.

Se ejecuta como proceso separado al servidor REST de Django
(ver Dockerfile / docker-compose.yml).

NOTA: Este archivo está listo para activarse cuando ya hayas generado los
stubs gRPC desde proto/notificaciones.proto con generate_protos.sh.
Por ahora solo levanta un servidor vacío para que el contenedor no falle.
"""
import os
import sys
from concurrent import futures
from pathlib import Path

import django
import grpc

# Configurar Django ANTES de importar modelos
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings  # noqa: E402

# TODO (cuando tengas los stubs generados):
# from grpc_server.services import NotificacionesServicer
# from protos import notificaciones_pb2_grpc


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # TODO: Registrar el servicer cuando tengas los stubs
    # notificaciones_pb2_grpc.add_NotificacionesServiceServicer_to_server(
    #     NotificacionesServicer(), server
    # )

    port = settings.GRPC_PORT
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"[ms-notificaciones] gRPC server escuchando en :{port}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
