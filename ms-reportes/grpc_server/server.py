"""
Servidor gRPC de ms-reportes.
Se ejecuta como proceso separado al servidor REST de Django.
"""
import os
import sys
import signal
from concurrent import futures
from pathlib import Path

import django
import grpc

# Configurar Django ANTES de importar modelos
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "protos"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings
from protos import reportes_pb2_grpc
from grpc_server.services import ReportesServicer


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    reportes_pb2_grpc.add_ReportesServiceServicer_to_server(ReportesServicer(), server)

    port = settings.GRPC_PORT
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"[ms-reportes] gRPC server escuchando en :{port}")

    # Cierre limpio con Ctrl+C o señal de Docker
    def _stop(signum, frame):
        print("[ms-reportes] Deteniendo gRPC server...")
        server.stop(grace=5).wait()

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT,  _stop)

    server.wait_for_termination()


if __name__ == "__main__":
    serve()