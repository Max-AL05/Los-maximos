"""
Servidor gRPC de ms-calificaciones.

Se ejecuta como proceso separado al servidor REST de Django 
(ver Dockerfile / docker-compose.yml) 
"""
import os
import sys
from concurrent import futures
from pathlib import Path

import django
import grpc

# 1. Configurar Django ANTES de importar modelos para cargar el entorno
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings

# 2. Importar el servicer y los archivos generados de gRPC
from grpc_server.services import CalificacionesServicer
import protos.calificaciones_pb2_grpc as calificaciones_pb2_grpc


def serve():
    """Inicia el servidor gRPC para MS-4 Calificaciones[cite: 191]."""
    # Crear el servidor con un pool de hilos para manejar peticiones concurrentes
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # 3. Registrar el servicer de Calificaciones en el servidor
    calificaciones_pb2_grpc.add_CalificacionesServiceServicer_to_server(
        CalificacionesServicer(), server
    )

    # 4. Configurar el puerto (Se recomienda rango 50051-50057) 
    # Si settings.GRPC_PORT no está definido, usamos 50054 por defecto para MS-4
    port = getattr(settings, "GRPC_PORT", "50054")
    
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    
    print(f"==========================================================")
    print(f"[ms-calificaciones] gRPC server escuchando en puerto: {port}")
    print(f"Arquitectura: Microservicios independientes (MS-4) ")
    print(f"==========================================================")
    
    # Mantener el proceso vivo
    server.wait_for_termination()


if __name__ == "__main__":
    try:
        serve()
    except KeyboardInterrupt:
        print("\n[ms-calificaciones] Servidor gRPC detenido por el usuario.")
        sys.exit(0)