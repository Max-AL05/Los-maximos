FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias del sistema:
#   build-essential / libpq-dev → para compilar psycopg2 binarios
#   curl → para los healthchecks de docker-compose
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Asegura que la carpeta protos/ exista incluso si los stubs aún no se generaron
RUN mkdir -p protos && touch protos/__init__.py

EXPOSE 8004 50054

# Healthcheck del lado HTTP (gRPC se valida con un script propio si quieres).
HEALTHCHECK --interval=20s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS http://localhost:8004/health/ || exit 1

# Entrypoint:
#   1) migra
#   2) collectstatic (para gunicorn + STATIC_ROOT)
#   3) levanta gRPC server en background
#   4) levanta gunicorn en foreground (4 workers — ajustar según CPU)
ENV PYTHONPATH="/app:/app/protos"

CMD python -m grpc_tools.protoc -I../proto --python_out=./protos --grpc_python_out=./protos ../proto/*.proto && \
    sed -i 's/import \(.*_pb2\) as/from . import \1 as/g' protos/*_pb2_grpc.py && \
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    python -m grpc_server.server & \
    python manage.py runserver 0.0.0.0:8004