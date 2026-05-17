"""
Serializers de validación de entrada y de salida.

En modo STANDALONE_MODE=True, los serializers de entrada esperan email/nombre
directamente en el body, ya que aún no se hacen llamadas gRPC a otros MS.
Cuando integres gRPC, podrás cambiar a recibir solo IDs.
"""
from rest_framework import serializers
from .models import Notificacion


# ============================================================================
# Entradas (lo que recibes en POST /notificaciones/...)
# ============================================================================

class BienvenidaSerializer(serializers.Serializer):
    """Email de bienvenida cuando se da de alta a un alumno."""
    alumno_id = serializers.UUIDField(required=False, allow_null=True)
    alumno_email = serializers.EmailField()
    alumno_nombre = serializers.CharField(max_length=200)
    materia_id = serializers.UUIDField(required=False, allow_null=True)
    materia_nombre = serializers.CharField(max_length=200)
    clave_unica = serializers.CharField(max_length=64)


class BajaSerializer(serializers.Serializer):
    """Aviso al docente de que un alumno se dio de baja."""
    alumno_id = serializers.UUIDField(required=False, allow_null=True)
    alumno_nombre = serializers.CharField(max_length=200)
    docente_id = serializers.UUIDField(required=False, allow_null=True)
    docente_email = serializers.EmailField()
    docente_nombre = serializers.CharField(max_length=200)
    materia_id = serializers.UUIDField(required=False, allow_null=True)
    materia_nombre = serializers.CharField(max_length=200)
    motivo = serializers.CharField(required=False, allow_blank=True, default="")


class AlumnoCierreSerializer(serializers.Serializer):
    """Sub-elemento usado dentro de CierreMateriaSerializer."""
    email = serializers.EmailField()
    nombre = serializers.CharField(max_length=200)
    calificacion_final = serializers.FloatField(required=False, allow_null=True)


class CierreMateriaSerializer(serializers.Serializer):
    """Notificación masiva al cerrar una materia (a todos los alumnos inscritos)."""
    materia_id = serializers.UUIDField(required=False, allow_null=True)
    materia_nombre = serializers.CharField(max_length=200)
    periodo = serializers.CharField(max_length=50, required=False, allow_blank=True, default="")
    alumnos = AlumnoCierreSerializer(many=True)


class ResetPasswordSerializer(serializers.Serializer):
    """Email con link para restablecer contraseña."""
    user_id = serializers.UUIDField(required=False, allow_null=True)
    user_email = serializers.EmailField()
    user_nombre = serializers.CharField(max_length=200)
    reset_link = serializers.URLField()


# ============================================================================
# Salidas (representación de la entidad Notificacion)
# ============================================================================

class NotificacionSerializer(serializers.ModelSerializer):
    """Salida: registro auditable de una notificación enviada."""
    class Meta:
        model = Notificacion
        fields = [
            "id",
            "tipo",
            "destinatario_email",
            "destinatario_user_id",
            "asunto",
            "payload",
            "estado",
            "error",
            "intentos",
            "created_at",
            "sent_at",
        ]
        read_only_fields = fields
