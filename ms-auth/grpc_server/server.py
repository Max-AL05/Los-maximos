"""
Servidor gRPC de ms-auth.

Se ejecuta como proceso separado al servidor REST de Django.
Ver Dockerfile / docker-compose.yml.
"""
import os
import sys
from concurrent import futures
from pathlib import Path

import django
import grpc

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings
from grpc_server.services import AuthServicer
from protos import auth_pb2_grpc


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthServicer(), server)

    port = settings.GRPC_PORT
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"[ms-auth] gRPC server escuchando en :{port}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()