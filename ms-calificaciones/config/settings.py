"""
Configuración Django para MS-4 Calificaciones.
 
Todas las variables sensibles se leen desde .env (ver .env.example).
NO hay credenciales hardcoded en este archivo.
"""
from pathlib import Path
import os
from datetime import timedelta
 
from dotenv import load_dotenv
 
load_dotenv()
 
BASE_DIR = Path(__file__).resolve().parent.parent
 
# ─────────────────────────────────────────────────────────────────────────────
# Núcleo
# ─────────────────────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "dev-insecure-change-me")
DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() == "true"
ALLOWED_HOSTS = [h.strip() for h in os.environ.get(
    "DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1"
).split(",") if h.strip()]
 
 
# ─────────────────────────────────────────────────────────────────────────────
# Apps
# ─────────────────────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
 
    # Terceros
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "drf_spectacular",
 
    # Apps locales
    "apps.ponderaciones",
    "apps.calificaciones",
]
 
 
# ─────────────────────────────────────────────────────────────────────────────
# Middleware  ─ El middleware JWT propio queda activo para validar tokens
# emitidos por MS-1 vía gRPC. Se puede apagar poniendo DISABLE_JWT_MIDDLEWARE=true
# en el .env (útil cuando MS-1 todavía no está arriba en el equipo).
# ─────────────────────────────────────────────────────────────────────────────
_DISABLE_JWT_MW = os.environ.get("DISABLE_JWT_MIDDLEWARE", "False").lower() == "true"
 
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
if not _DISABLE_JWT_MW:
    MIDDLEWARE.append("apps.calificaciones.middleware.JWTAuthMiddleware")
 
 
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
 
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
 
 
# ─────────────────────────────────────────────────────────────────────────────
# Base de datos – PostgreSQL leído 100 % desde el entorno.
# Sin valores por default sensibles: si falta una variable, falla en arranque
# (mejor que correr accidentalmente con SQLite en producción).
# ─────────────────────────────────────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends.postgresql"),
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": os.environ.get("DB_HOST", "db-calificaciones"),
        "PORT": os.environ.get("DB_PORT", "5432"),
        # Reconexiones automáticas si Postgres se reinicia
        "CONN_MAX_AGE": int(os.environ.get("DB_CONN_MAX_AGE", 60)),
    }
}
 
 
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
 
 
# ─────────────────────────────────────────────────────────────────────────────
# i18n / static
# ─────────────────────────────────────────────────────────────────────────────
LANGUAGE_CODE = "es-mx"
TIME_ZONE = "America/Mexico_City"
USE_I18N = True
USE_TZ = True
 
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"   # gunicorn / collectstatic
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
 
 
# ─────────────────────────────────────────────────────────────────────────────
# DRF
# ─────────────────────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    # Cuando el middleware JWT propio está activo, ya valida en cada request.
    # Aquí dejamos AllowAny porque el middleware ya cortó las no-autenticadas.
    # Si quieres seguridad en doble capa (recomendado), pon IsAuthenticated:
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny" if _DISABLE_JWT_MW
        else "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}
 
 
# ─────────────────────────────────────────────────────────────────────────────
# SimpleJWT – el SIGNING_KEY DEBE ser idéntico al de MS-1 Auth.
# ─────────────────────────────────────────────────────────────────────────────
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.environ.get("JWT_ACCESS_TTL_MIN", 60))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.environ.get("JWT_REFRESH_TTL_DAYS", 7))),
    "ALGORITHM": os.environ.get("JWT_ALGORITHM", "HS256"),
    "SIGNING_KEY": os.environ["JWT_SECRET_KEY"],   # OBLIGATORIO; falla si falta
    "AUTH_HEADER_TYPES": ("Bearer",),
}
 
 
# ─────────────────────────────────────────────────────────────────────────────
# CORS – ya no abrimos a todos por default. Sólo los orígenes en .env.
# ─────────────────────────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    o.strip() for o in os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")
    if o.strip()
]
# Bloque de escape para desarrollo: si CORS_ALLOWED_ORIGINS está vacío y DEBUG=True,
# permitimos todo. En producción nunca abrir.
CORS_ALLOW_ALL_ORIGINS = DEBUG and not CORS_ALLOWED_ORIGINS
CORS_ALLOW_CREDENTIALS = True
 
 
# ─────────────────────────────────────────────────────────────────────────────
# gRPC – endpoints de los demás MS y nuestro propio puerto de servidor.
# Convención: en Docker los hostnames son los nombres del servicio en compose.
# ─────────────────────────────────────────────────────────────────────────────
GRPC_TARGETS = {
    "auth":           os.environ.get("GRPC_AUTH_URL",           "ms-auth:50051"),
    "periodos":       os.environ.get("GRPC_PERIODOS_URL",       "ms-periodos:50052"),
    "alumnos":        os.environ.get("GRPC_ALUMNOS_URL",        "ms-alumnos:50053"),
    "calificaciones": os.environ.get("GRPC_CALIFICACIONES_URL", "ms-calificaciones:50054"),
    "asistencias":    os.environ.get("GRPC_ASISTENCIAS_URL",    "ms-asistencias:50055"),
    "notificaciones": os.environ.get("GRPC_NOTIFICACIONES_URL", "ms-notificaciones:50056"),
    "reportes":       os.environ.get("GRPC_REPORTES_URL",       "ms-reportes:50057"),
}
# Timeout (segundos) que aplica a CADA llamada gRPC saliente.
# Sin esto, una llamada a un MS caído puede colgar el request HTTP entrante.
GRPC_DEFAULT_TIMEOUT = float(os.environ.get("GRPC_TIMEOUT_SEC", 5))
GRPC_PORT = int(os.environ.get("GRPC_PORT", 50054))
 
 
# ─────────────────────────────────────────────────────────────────────────────
# Spectacular
# ─────────────────────────────────────────────────────────────────────────────
SPECTACULAR_SETTINGS = {
    "TITLE": "MS-4 Calificaciones",
    "DESCRIPTION": "Microservicio de calificaciones y ponderaciones del sistema AGM",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}
 
 
# ─────────────────────────────────────────────────────────────────────────────
# Logging mínimo para que los warnings de los clients gRPC no se pierdan
# ─────────────────────────────────────────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[{asctime}] {levelname} {name} :: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "default"},
    },
    "root": {"handlers": ["console"], "level": os.environ.get("LOG_LEVEL", "INFO")},
}