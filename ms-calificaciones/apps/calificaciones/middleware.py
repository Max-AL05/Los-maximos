import logging
import grpc
from django.http import JsonResponse
from .auth_client import AuthClient

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
        self.auth_client = AuthClient()

    def __call__(self, request):
        if any(request.path.startswith(p) for p in _EXEMPT_PATHS):
            return self.get_response(request)

        auth_header = request.headers.get("Authorization", "")
        parts = auth_header.split(" ", 1)
        if len(parts) != 2 or parts[0] != "Bearer" or not parts[1].strip():
            return _json_error("Cabecera de autorización faltante o formato inválido (Bearer <token>).", 401)
        
        token = parts[1].strip()

        try:
            is_valid, claims = self.auth_client.validar_token(token)
        except grpc.RpcError as e:
            code = e.code() if hasattr(e, "code") else None
            if code in (grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.DEADLINE_EXCEEDED):
                logger.error("[JWTAuthMiddleware] MS-1 inalcanzable: %s", code)
                return _json_error("Servicio de autenticación no disponible. Reintenta en unos segundos.", 503)
            logger.error("[JWTAuthMiddleware] Error gRPC inesperado: %s", e)
            return _json_error("Error al validar el token.", 500)
        except Exception as e:
            logger.exception("[JWTAuthMiddleware] Error inesperado: %s", e)
            return _json_error("Error interno al procesar la autenticación.", 500)

        if not is_valid:
            return _json_error("Acceso denegado: token inválido, expirado o revocado.", 401)

        request.user_id = claims.user_id
        request.user_role = claims.role
        request.user_email = claims.email

        return self.get_response(request)