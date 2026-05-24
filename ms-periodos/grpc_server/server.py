"""
Servidor gRPC de ms-periodos.
Se ejecuta como proceso separado al servidor REST de Django.
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
from grpc_server.services import PeriodosServicer
from protos import periodos_pb2_grpc


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    periodos_pb2_grpc.add_PeriodosServiceServicer_to_server(PeriodosServicer(), server)

    port = settings.GRPC_PORT
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"[ms-periodos] gRPC server escuchando en :{port}")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()