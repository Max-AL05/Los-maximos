"""Serializers para Asistencias."""
from rest_framework import serializers
from .models import Asistencia


class RegistrarAsistenciaSerializer(serializers.Serializer):
    """Validación para registrar asistencia por QR."""
    sesion_id = serializers.UUIDField()
    qr_token = serializers.CharField(max_length=36)  # UUID como string


class AsistenciaSerializer(serializers.ModelSerializer):
    """Serializer de lectura para Asistencia."""

    class Meta:
        model = Asistencia
        fields = [
            'id', 'sesion', 'alumno_id', 'materia_id', 'fecha', 'estado'
        ]
        read_only_fields = ['id', 'fecha']