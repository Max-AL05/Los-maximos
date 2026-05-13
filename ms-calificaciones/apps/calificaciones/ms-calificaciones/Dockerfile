FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p protos && touch protos/__init__.py

EXPOSE 8004 50054

HEALTHCHECK --interval=20s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS http://localhost:8004/health/ || exit 1

CMD ["sh", "-c", "\
    python manage.py migrate --noinput && \
    python manage.py collectstatic --noinput && \
    python -m grpc_server.server & \
    gunicorn config.wsgi:application \
        --bind 0.0.0.0:8004 \
        --workers ${GUNICORN_WORKERS:-4} \
        --access-logfile - \
        --error-logfile - \
"]