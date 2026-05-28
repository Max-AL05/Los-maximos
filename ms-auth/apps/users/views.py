"""
Views REST de MS-1 Auth & Users.

Endpoints expuestos al cliente:
    POST /auth/register
    POST /auth/login
    POST /auth/refresh-token
    POST /auth/forgot-password
    POST /auth/reset-password
    GET  /auth/me

Todas las respuestas siguen el formato estándar:
    { "success": bool, "data": {...}, "message": "..." }
"""
import secrets
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import PasswordResetToken, User
from .serializers import (
    CustomTokenObtainPairSerializer,
    ForgotPasswordSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UserMeSerializer,
)


@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
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


class LoginView(TokenObtainPairView):
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


class RefreshTokenView(TokenRefreshView):
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


@api_view(["POST"])
@permission_classes([AllowAny])
def forgot_password_view(request):
    """
    Genera un PasswordResetToken de un solo uso (TTL 30 min) y llama
    a MS-6 via gRPC para que envíe el correo con el enlace.
    Siempre responde 200 para no revelar si el email existe.
    """
    serializer = ForgotPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data["email"]

    try:
        user = User.objects.get(email=email, is_active=True)
    except User.DoesNotExist:
        return Response(
            {"success": True, "data": None, "message": "Si el correo existe recibirás un enlace en breve"},
            status=status.HTTP_200_OK,
        )

    # Invalida tokens previos no usados del mismo usuario
    PasswordResetToken.objects.filter(user=user, used=False).update(used=True)

    raw_token = secrets.token_urlsafe(48)
    expires_at = timezone.now() + timedelta(minutes=30)
    PasswordResetToken.objects.create(
        user=user,
        token=raw_token,
        expires_at=expires_at,
    )

    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"

    # ── Publicar evento asíncrono via RabbitMQ (MS-6 lo consume) ──────────
    # Usamos bus de eventos en lugar de gRPC síncrono: si MS-6 cae,
    # el mensaje queda en la cola y se reintenta cuando vuelva a levantar.
    try:
        from shared.rabbitmq.publisher import publish_event
        from shared.rabbitmq.events import AUTH_RESET_PASSWORD
        publish_event(AUTH_RESET_PASSWORD, {
            "user_id":     str(user.id),
            "user_email":  user.email,
            "user_nombre": user.nombre_completo,
            "reset_link":  reset_link,
        })
    except Exception:
        pass  # El sistema sigue operando aunque RabbitMQ no esté disponible

    return Response(
        {"success": True, "data": None, "message": "Si el correo existe recibirás un enlace en breve"},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password_view(request):
    """
    Valida el token, actualiza la contraseña y marca el token como usado.
    """
    serializer = ResetPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    raw_token = serializer.validated_data["token"]
    new_password = serializer.validated_data["new_password"]

    try:
        reset_token = PasswordResetToken.objects.select_related("user").get(
            token=raw_token,
            used=False,
            expires_at__gt=timezone.now(),
        )
    except PasswordResetToken.DoesNotExist:
        return Response(
            {"success": False, "data": None, "message": "Token inválido o expirado"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = reset_token.user
    user.set_password(new_password)
    user.save(update_fields=["password"])

    reset_token.used = True
    reset_token.save(update_fields=["used"])

    return Response(
        {"success": True, "data": None, "message": "Contraseña actualizada correctamente"},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_view(request):
    return Response(
        {
            "success": True,
            "data": UserMeSerializer(request.user).data,
            "message": "",
        },
        status=status.HTTP_200_OK,
    )