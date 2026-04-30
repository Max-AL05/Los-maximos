"""
Views REST de MS-1 Auth & Users.

Endpoints expuestos al cliente:
    POST /auth/login
    POST /auth/refresh-token
    POST /auth/forgot-password
    POST /auth/reset-password
    GET  /auth/me
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import (
    LoginSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    UserMeSerializer,
)


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """POST /auth/login → access + refresh JWT."""
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    # TODO: autenticar con email/password, generar JWT incluyendo role
    return Response(
        {"success": True, "data": {"access": "", "refresh": ""}, "message": "TODO"},
        status=status.HTTP_200_OK,
    )


# POST /auth/refresh-token
refresh_token_view = TokenRefreshView.as_view()


@api_view(["POST"])
@permission_classes([AllowAny])
def forgot_password_view(request):
    """POST /auth/forgot-password → genera token y solicita envío de correo a MS-6."""
    serializer = ForgotPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    # TODO: crear PasswordResetToken, llamar gRPC SendResetPassword a MS-6
    return Response({"success": True, "message": "TODO"}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password_view(request):
    """POST /auth/reset-password → consume token y actualiza contraseña."""
    serializer = ResetPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    # TODO: validar token (no usado, no expirado), actualizar contraseña, marcar used=True
    return Response({"success": True, "message": "TODO"}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_view(request):
    """GET /auth/me → datos del usuario autenticado."""
    return Response(
        {"success": True, "data": UserMeSerializer(request.user).data, "message": ""},
        status=status.HTTP_200_OK,
    )
