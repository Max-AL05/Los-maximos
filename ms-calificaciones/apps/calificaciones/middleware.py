import grpc
from django.http import JsonResponse
from .auth_client import AuthClient

class JWTAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.auth_client = AuthClient()

    def __call__(self, request):
        # 1. Excluir rutas que no requieren autenticación
        # Agregamos /api/docs o similares si usas Swagger/OpenAPI
        exempt_paths = ['/admin/', '/api/schema/', '/api/docs/']
        if any(request.path.startswith(path) for path in exempt_paths):
            return self.get_response(request)

        # 2. Extracción segura del token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({
                "success": False, 
                "message": "Cabecera de autorización faltante o formato inválido (Bearer <token>)."
            }, status=401)

        try:
            parts = auth_header.split(' ')
            if len(parts) != 2:
                raise ValueError("Token mal formado.")
            token = parts[1]

            # 3. Validar con el MS-1 vía gRPC con manejo de errores de conexión
            is_valid, user_claims = self.auth_client.validar_token(token)

            if not is_valid:
                return JsonResponse({
                    "success": False, 
                    "message": "Acceso denegado: Token inválido, expirado o revocado."
                }, status=401)

            # 4. Inyectar datos en la request de forma segura
            # Usamos atributos que no choquen con los de Django Auth si se usa a la par
            request.user_id = user_claims.user_id
            request.user_role = user_claims.role  # Administrador, Docente o Alumno

        except ValueError as e:
            return JsonResponse({"success": False, "message": str(e)}, status=401)
        except grpc.RpcError as e:
            # Si el MS-1 (Auth) está caído, devolvemos un 503 (Servicio no disponible)
            return JsonResponse({
                "success": False, 
                "message": "Error de comunicación con el servicio de autenticación."
            }, status=503)
        except Exception as e:
            return JsonResponse({
                "success": False, 
                "message": "Error interno al procesar la autenticación."
            }, status=500)

        return self.get_response(request)