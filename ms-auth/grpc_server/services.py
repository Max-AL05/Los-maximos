"""
Servicers gRPC de MS-1 Auth & Users.

Implementan los métodos del contrato auth.proto:
    - ValidateToken  → decodifica el JWT y devuelve los claims
    - GetUserById    → busca un usuario por UUID
    - CheckRole      → verifica si el usuario tiene el rol indicado
"""
import grpc
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken

from apps.users.models import User
from protos import auth_pb2, auth_pb2_grpc


class AuthServicer(auth_pb2_grpc.AuthServiceServicer):

    def ValidateToken(self, request, context):
        """
        Decodifica el JWT con la clave configurada en SIMPLE_JWT.
        Devuelve is_valid=True si el token es correcto, False si no.
        """
        try:
            token = UntypedToken(request.token)
            payload = token.payload
            return auth_pb2.UserClaims(
                user_id=str(payload.get("user_id", "")),
                email=str(payload.get("email", "")),
                role=str(payload.get("role", "")),
                is_valid=True,
                exp=int(payload.get("exp", 0)),
            )
        except (InvalidToken, TokenError):
            return auth_pb2.UserClaims(is_valid=False)
        except Exception:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Error interno al validar el token")
            return auth_pb2.UserClaims(is_valid=False)

    def GetUserById(self, request, context):
        """
        Busca el usuario por UUID.
        Devuelve UserProfile vacío + NOT_FOUND si no existe.
        """
        try:
            user = User.objects.get(id=request.user_id)
            return auth_pb2.UserProfile(
                user_id=str(user.id),
                email=user.email,
                nombre_completo=user.nombre_completo,
                role=user.role,
                is_active=user.is_active,
            )
        except User.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Usuario {request.user_id} no encontrado")
            return auth_pb2.UserProfile()
        except Exception:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Error interno al buscar el usuario")
            return auth_pb2.UserProfile()

    def CheckRole(self, request, context):
        """
        Verifica si el usuario tiene el rol indicado.
        Devuelve has_role=False si el usuario no existe.
        """
        try:
            user = User.objects.get(id=request.user_id, is_active=True)
            return auth_pb2.CheckRoleResponse(has_role=(user.role == request.role))
        except User.DoesNotExist:
            return auth_pb2.CheckRoleResponse(has_role=False)
        except Exception:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Error interno al verificar el rol")
            return auth_pb2.CheckRoleResponse(has_role=False)