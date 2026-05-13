"""
Serializers para el módulo de asistencias.
"""
from rest_framework import serializers
from .models import Asistencia


class RegistrarAsistenciaSerializer(serializers.Serializer):
    """Valida el body de POST /asistencias/registrar."""
    sesion_id = serializers.UUIDField()
    qr_token = serializers.CharField(max_length=2048)


class AsistenciaSerializer(serializers.ModelSerializer):
    """Serializa un registro de Asistencia hacia el cliente REST."""

    class Meta:
        model = Asistencia
        fields = [
            "id",
            "sesion_id",
            "alumno_id",
            "materia_id",
            "fecha",
            "estado",
            # qr_token_hash se omite por seguridad (es dato de auditoría interna)
        ]
        read_only_fields = fields