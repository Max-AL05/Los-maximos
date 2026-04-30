FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias del sistema (psycopg2 necesita libpq-dev y build-essentials)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Generar código gRPC desde los .proto montados
RUN mkdir -p protos && touch protos/__init__.py

EXPOSE 8004 50054

# El entrypoint levanta REST (gunicorn/runserver) y gRPC en paralelo.
# Ajustar en producción: usar gunicorn + un proceso supervisor (honcho/supervisord).
CMD ["sh", "-c", "python manage.py migrate --noinput && (python -m grpc_server.server &) && python manage.py runserver 0.0.0.0:8004"]
