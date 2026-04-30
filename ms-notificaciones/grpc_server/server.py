"""
Servidor gRPC de ms-notificaciones.

Se ejecuta como proceso separado al servidor REST de Django
(ver Dockerfile / docker-compose.yml).
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

# TODO: Importar el servicer correspondiente desde grpc_server.services
# from grpc_server.services import MyServicer
# from protos import <ms>_pb2_grpc


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # TODO: Registrar servicers
    # <ms>_pb2_grpc.add_<MS>ServiceServicer_to_server(MyServicer(), server)

    port = settings.GRPC_PORT
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"[ms-notificaciones] gRPC server escuchando en :{port}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
