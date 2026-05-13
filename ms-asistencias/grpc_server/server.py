"""
Servidor gRPC de MS-5 Asistencias QR.

Se levanta como proceso SEPARADO al servidor REST de Django.
Puerto: 50055 (configurado en settings.GRPC_PORT / variable GRPC_PORT)

Inicio manual:
    cd ms-asistencias
    python grpc_server/server.py

En Docker, el Dockerfile debe tener un comando de entrada que levante
tanto el servidor REST (gunicorn/manage.py runserver) como este proceso gRPC.
"""
import os
import sys
from concurrent import futures
from pathlib import Path

import django
import grpc

# ---------------------------------------------------------------------------
# Configurar Django ANTES de importar cualquier modelo o servicer.
# Necesario porque los servicers usan el ORM de Django.
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings  # noqa: E402 (import después de django.setup())

# Importar el servicer y los stubs generados por protoc
from grpc_server.services import AsistenciasServicer            # noqa: E402
from protos import asistencias_pb2_grpc                         # noqa: E402


def serve():
    """
    Inicializa y arranca el servidor gRPC con el servicer de asistencias.

    - Max workers: 10 (suficiente para carga académica normal)
    - Puerto: definido en settings.GRPC_PORT (default 50055)
    - Sin TLS (insecure_port); en producción agregar credenciales SSL
    """
    # Crear servidor con pool de hilos
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            # Opciones de rendimiento/estabilidad recomendadas
            ("grpc.max_receive_message_length", 10 * 1024 * 1024),   # 10 MB
            ("grpc.max_send_message_length", 10 * 1024 * 1024),      # 10 MB
            ("grpc.keepalive_time_ms", 30000),                        # keepalive cada 30s
        ],
    )

    # Registrar el servicer de asistencias en el servidor
    asistencias_pb2_grpc.add_AsistenciasServiceServicer_to_server(
        AsistenciasServicer(),
        server,
    )

    # Leer el puerto desde settings (que lo toma de la variable de entorno GRPC_PORT)
    port = settings.GRPC_PORT   # Por defecto: 50055 (ver .env.example)
    server.add_insecure_port(f"[::]:{port}")

    server.start()
    print(f"[ms-asistencias] ✓ gRPC server escuchando en :{port}")
    print("[ms-asistencias]   Servicers registrados: AsistenciasService")
    print("[ms-asistencias]   Métodos disponibles:")
    print("[ms-asistencias]     - GetAsistenciaAlumno(alumno_id, materia_id)")
    print("[ms-asistencias]     - GetEstadisticasAsistencia(materia_id)")

    # Bloquear el hilo principal hasta que el servidor sea detenido
    server.wait_for_termination()


if __name__ == "__main__":
    serve()