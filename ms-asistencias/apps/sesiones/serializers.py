"""Serializers para Sesiones."""
from rest_framework import serializers
from .models import Sesion, EstadoSesion


class IniciarSesionSerializer(serializers.Serializer):
    """Validación para iniciar sesión."""
    materia_id = serializers.CharField(max_length=64)
    duracion_minutos = serializers.IntegerField(default=10, min_value=5, max_value=60)
    umbral_retardo_min = serializers.IntegerField(default=5, min_value=1, max_value=9)

    def validate(self, data):
        if data['umbral_retardo_min'] >= data['duracion_minutos']:
            raise serializers.ValidationError(
                "umbral_retardo_min debe ser menor que duracion_minutos"
            )
        return data


class SesionSerializer(serializers.ModelSerializer):
    """Serializer de lectura para Sesion."""
    fin = serializers.SerializerMethodField()

    class Meta:
        model = Sesion
        fields = [
            'id', 'materia_id', 'docente_id', 'inicio', 'fin',
            'duracion_minutos', 'umbral_retardo_min', 'estado'
        ]
        read_only_fields = ['id', 'inicio']

    def get_fin(self, obj):
        return obj.fin.isoformat()