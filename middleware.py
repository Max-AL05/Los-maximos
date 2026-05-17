"""
Middleware JWT.

Cada request entrante (excepto rutas públicas) debe traer el header
    Authorization: Bearer <jwt>

El middleware llama a MS-1 vía gRPC para validar. Posibles respuestas:

    | situación                     | status |
    |-------------------------------|--------|
    | header faltante / mal formado | 401    |
    | token inválido / expirado     | 401    |
    | MS-1 caído / unreachable      | 503    |
    | error inesperado del cliente  | 500    |

Es importante distinguir 401 de 503: 401 le dice al cliente "tu token está
mal", 503 le dice "el sistema de auth no está disponible, reintenta". Si los
mezcláramos, un alumno con token bueno vería 401 cuando MS-1 se reinicia.
"""
import logging

import grpc
from django.http import JsonResponse

from .auth_client import AuthClient


logger = logging.getLogger(__name__)


# Rutas que NO requieren JWT.
# /admin/ y /api/docs/ son herramientas de soporte; /health/ es para
# probes de Docker/Kubernetes.
_EXEMPT_PATHS = (
    "/admin/",
    "/api/schema/",
    "/api/docs/",
    "/health/",
)


def _json_error(message: str, status: int) -> JsonResponse:
    return JsonResponse({"success": False, "message": message}, status=status)


class JWTAuthMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
        # Cliente reutilizable (un solo canal gRPC compartido).
        self.auth_client = AuthClient()

    def __call__(self, request):
        # Bypass para rutas públicas.
        if any(request.path.startswith(p) for p in _EXEMPT_PATHS):
            return self.get_response(request)

        # 1) Cabecera presente y bien formada.
        auth_header = request.headers.get("Authorization", "")
        parts = auth_header.split(" ", 1)
        if len(parts) != 2 or parts[0] != "Bearer" or not parts[1].strip():
            return _json_error(
                "Cabecera de autorización faltante o formato inválido (Bearer <token>).",
                401,
            )
        token = parts[1].strip()

        # 2) Llamada a MS-1.
        try:
            is_valid, claims = self.auth_client.validar_token(token)
        except grpc.RpcError as e:
            code = e.code() if hasattr(e, "code") else None
            # UNAVAILABLE / DEADLINE_EXCEEDED → MS-1 está caído o lento.
            if code in (grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.DEADLINE_EXCEEDED):
                logger.error("[JWTAuthMiddleware] MS-1 inalcanzable: %s", code)
                return _json_error(
                    "Servicio de autenticación no disponible. Reintenta en unos segundos.",
                    503,
                )
            logger.error("[JWTAuthMiddleware] Error gRPC inesperado: %s", e)
            return _json_error("Error al validar el token.", 500)
        except Exception as e:
            logger.exception("[JWTAuthMiddleware] Error inesperado: %s", e)
            return _json_error("Error interno al procesar la autenticación.", 500)

        if not is_valid:
            return _json_error(
                "Acceso denegado: token inválido, expirado o revocado.",
                401,
            )

        # 3) Inyectar claims en la request.
        # NO usamos request.user para no chocar con django.contrib.auth.
        request.user_id   = claims.user_id
        request.user_role = claims.role     # ADMIN | DOCENTE | ALUMNO
        request.user_email = claims.email

        return self.get_response(request)