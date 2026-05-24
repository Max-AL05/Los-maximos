"""
Configuración Django para el microservicio.
"""

from pathlib import Path
import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "dev-insecure-change-me"
)

DEBUG = (
    os.environ.get(
        "DJANGO_DEBUG",
        "True"
    ).lower() == "true"
)

ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS",
    "*"
).split(",")


# ─────────────────────────────────────────────
# APPS
# ─────────────────────────────────────────────

INSTALLED_APPS = [

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "drf_spectacular",

    "apps.periodos",
    "apps.materias",
]


# ─────────────────────────────────────────────
# MIDDLEWARE
# ─────────────────────────────────────────────

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


ROOT_URLCONF = "config.urls"

WSGI_APPLICATION = "config.wsgi.application"

ASGI_APPLICATION = "config.asgi.application"


# ─────────────────────────────────────────────
# TEMPLATES
# ─────────────────────────────────────────────

TEMPLATES = [
    {
        "BACKEND":
            "django.template.backends.django.DjangoTemplates",

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


# ─────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────

DATABASES = {

    "default": {

        "ENGINE": os.environ.get(
            "DB_ENGINE",
            "django.db.backends.postgresql"
        ),

        "NAME": os.environ.get(
            "DB_NAME",
            "agm_db"
        ),

        "USER": os.environ.get(
            "DB_USER",
            "agm_user"
        ),

        "PASSWORD": os.environ.get(
            "DB_PASSWORD",
            "agm_password"
        ),

        "HOST": os.environ.get(
            "DB_HOST",
            "localhost"
        ),

        "PORT": os.environ.get(
            "DB_PORT",
            "5432"
        ),
    }
}


# ─────────────────────────────────────────────
# PASSWORDS
# ─────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = [

    {
        "NAME":
            "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },

    {
        "NAME":
            "django.contrib.auth.password_validation.MinimumLengthValidator"
    },

    {
        "NAME":
            "django.contrib.auth.password_validation.CommonPasswordValidator"
    },

    {
        "NAME":
            "django.contrib.auth.password_validation.NumericPasswordValidator"
    },
]


# ─────────────────────────────────────────────
# I18N
# ─────────────────────────────────────────────

LANGUAGE_CODE = "es-mx"

TIME_ZONE = "America/Mexico_City"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ─────────────────────────────────────────────
# DRF
# ─────────────────────────────────────────────

REST_FRAMEWORK = {

    "DEFAULT_AUTHENTICATION_CLASSES": (

        "common.authentication.StatelessJWTAuthentication",
    ),

    "DEFAULT_PERMISSION_CLASSES": (

        "rest_framework.permissions.IsAuthenticated",
    ),

    "DEFAULT_PAGINATION_CLASS":

        "rest_framework.pagination.PageNumberPagination",

    "PAGE_SIZE": 10,

    "DEFAULT_RENDERER_CLASSES": (

        "rest_framework.renderers.JSONRenderer",
    ),

    "DEFAULT_SCHEMA_CLASS":

        "drf_spectacular.openapi.AutoSchema",
}


# ─────────────────────────────────────────────
# JWT
# ─────────────────────────────────────────────

SIMPLE_JWT = {

    "USER_ID_FIELD": "id",

    "USER_ID_CLAIM": "user_id",

    "ACCESS_TOKEN_LIFETIME": timedelta(

        minutes=int(
            os.environ.get(
                "JWT_ACCESS_TTL_MIN",
                60
            )
        )
    ),

    "REFRESH_TOKEN_LIFETIME": timedelta(

        days=int(
            os.environ.get(
                "JWT_REFRESH_TTL_DAYS",
                7
            )
        )
    ),

    "ALGORITHM": os.environ.get(
        "JWT_ALGORITHM",
        "HS256"
    ),

    "SIGNING_KEY": os.environ.get(
        "JWT_SECRET_KEY",
        SECRET_KEY
    ),

    "AUTH_HEADER_TYPES": ("Bearer",),
}


# ─────────────────────────────────────────────
# CORS
# ─────────────────────────────────────────────

CORS_ALLOWED_ORIGINS = [

    o.strip()

    for o in os.environ.get(
        "CORS_ALLOWED_ORIGINS",
        ""
    ).split(",")

    if o.strip()
]

CORS_ALLOW_CREDENTIALS = True


# ─────────────────────────────────────────────
# SWAGGER
# ─────────────────────────────────────────────

SPECTACULAR_SETTINGS = {

    "TITLE":
        "AGM Microservicio",

    "DESCRIPTION":
        "API REST del microservicio AGM",

    "VERSION":
        "1.0.0",

    "SERVE_INCLUDE_SCHEMA": False,
}