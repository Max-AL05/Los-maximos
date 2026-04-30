from rest_framework import serializers
from .models import Notificacion


class BienvenidaSerializer(serializers.Serializer):
    alumno_id = serializers.UUIDField()
    materia_id = serializers.UUIDField()
    clave_unica = serializers.CharField()


class BajaSerializer(serializers.Serializer):
    alumno_id = serializers.UUIDField()
    docente_id = serializers.UUIDField()
    materia_id = serializers.UUIDField()


class CierreMateriaSerializer(serializers.Serializer):
    materia_id = serializers.UUIDField()


class ResetPasswordSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    reset_link = serializers.URLField()


class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = "__all__"
        read_only_fields = "__all__"
