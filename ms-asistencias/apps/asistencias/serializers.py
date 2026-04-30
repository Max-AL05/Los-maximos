from rest_framework import serializers
from .models import Asistencia


class RegistrarAsistenciaSerializer(serializers.Serializer):
    sesion_id = serializers.UUIDField()
    qr_token = serializers.CharField()  # token cifrado generado por el alumno


class AsistenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asistencia
        fields = "__all__"
        read_only_fields = ("id", "fecha", "estado")
