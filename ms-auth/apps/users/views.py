"""
Views REST de MS-1 Auth & Users.

Endpoints expuestos al cliente:
    POST /auth/register         (crear usuario – dev/testing)
    POST /auth/login            (devuelve access + refresh JWT)
    POST /auth/refresh-token    (renueva el access usando el refresh)
    POST /auth/forgot-password  (TODO – pendiente integración MS-6)
    POST /auth/reset-password   (TODO – pendiente)
    GET  /auth/me               (datos del usuario autenticado)

Todas las respuestas siguen el formato estándar del proyecto:
    { "success": bool, "data": {...}, "message": "..." }
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError # type: ignore
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView # type: ignore

from .serializers import (
    CustomTokenObtainPairSerializer,
    ForgotPasswordSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UserMeSerializer,
)


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------
@api_view(["POST"])
@permission_classes([AllowAny])  # ⚠️ DEV ONLY – en producción: IsAuthenticated + role=ADMIN
def register_view(request):
    """
    POST /auth/register

    Body JSON:
        {
            "email": "...",
            "password": "...",
            "role": "ADMIN" | "DOCENTE" | "ALUMNO",
            "nombre_completo": "...",
            "matricula": "..."   (sólo si role=ALUMNO),
            "cubiculo": "..."    (opcional, sólo docentes)
        }
    """
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response(
        {
            "success": True,
            "data": RegisterSerializer(user).data,
            "message": "Usuario creado exitosamente",
        },
        status=status.HTTP_201_CREATED,
    )


# ---------------------------------------------------------------------------
# Login (POST /auth/login)
# ---------------------------------------------------------------------------
class LoginView(TokenObtainPairView):
    """
    Devuelve `access`, `refresh` y datos del usuario.

    El access incluye los claims: user_id, role, email, nombre_completo.
    Esto permite que MS-2..MS-7 validen el rol sin llamar al MS-1.
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except (AuthenticationFailed, TokenError):
            return Response(
                {"success": False, "data": None, "message": "Credenciales inválidas"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(
            {
                "success": True,
                "data": serializer.validated_data,
                "message": "Inicio de sesión exitoso",
            },
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# Refresh token (POST /auth/refresh-token)
# ---------------------------------------------------------------------------
class RefreshTokenView(TokenRefreshView):
    """Body: {"refresh": "<refresh_token>"} → {"access": "<nuevo_access>"}"""

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
        except (TokenError, AuthenticationFailed):
            return Response(
                {"success": False, "data": None, "message": "Refresh token inválido o expirado"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(
            {"success": True, "data": response.data, "message": "Token renovado"},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# Forgot / Reset password (TODOs – dependen de MS-6 Notificaciones)
# ---------------------------------------------------------------------------
@api_view(["POST"])
@permission_classes([AllowAny])
def forgot_password_view(request):
    """POST /auth/forgot-password – genera token y solicita envío de correo a MS-6."""
    serializer = ForgotPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    # TODO: crear PasswordResetToken, llamar gRPC SendResetPassword a MS-6
    return Response(
        {"success": True, "data": None, "message": "Pendiente: integración con MS-6"},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password_view(request):
    """POST /auth/reset-password – consume token y actualiza contraseña."""
    serializer = ResetPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    # TODO: validar token, actualizar contraseña, marcar used=True
    return Response(
        {"success": True, "data": None, "message": "Pendiente: integración con MS-6"},
        status=status.HTTP_200_OK,
    )


# ---------------------------------------------------------------------------
# Me (GET /auth/me)
# ---------------------------------------------------------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_view(request):
    """GET /auth/me – datos del usuario autenticado (lee el JWT del header)."""
    return Response(
        {
            "success": True,
            "data": UserMeSerializer(request.user).data,
            "message": "",
        },
        status=status.HTTP_200_OK,
    )
