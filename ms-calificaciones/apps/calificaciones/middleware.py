"""
Middleware JWT — versión sin gRPC.
Valida el token JWT localmente sin llamar a MS-1.
"""
import logging
import os

import jwt
from django.http import JsonResponse

logger = logging.getLogger(__name__)

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
        self.secret    = os.environ.get("JWT_SECRET_KEY", "")
        self.algorithm = os.environ.get("JWT_ALGORITHM", "HS256")

    def __call__(self, request):
        if any(request.path.startswith(p) for p in _EXEMPT_PATHS):
            return self.get_response(request)

        auth_header = request.headers.get("Authorization", "")
        parts = auth_header.split(" ", 1)
        if len(parts) != 2 or parts[0] != "Bearer" or not parts[1].strip():
            return _json_error("Cabecera de autorización faltante o formato inválido.", 401)

        token = parts[1].strip()

        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            return _json_error("Token expirado.", 401)
        except jwt.InvalidTokenError:
            return _json_error("Token inválido.", 401)
        except Exception as e:
            logger.exception("Error inesperado al validar token: %s", e)
            return _json_error("Error interno al procesar la autenticación.", 500)

        request.user_id    = payload.get("sub") or payload.get("user_id", "")
        request.user_role  = payload.get("role", "")
        request.user_email = payload.get("email", "")

        return self.get_response(request)