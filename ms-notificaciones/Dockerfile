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

# Carpeta vacía para los stubs gRPC que se generen luego
RUN mkdir -p protos && touch protos/__init__.py

EXPOSE 8006 50056

# Migraciones + REST en 8006. El gRPC se activa cuando descomentes en server.py
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8006"]
