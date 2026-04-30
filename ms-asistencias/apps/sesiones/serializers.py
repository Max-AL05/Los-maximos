from rest_framework import serializers
from .models import Sesion


class IniciarSesionSerializer(serializers.Serializer):
    materia_id = serializers.UUIDField()
    duracion_minutos = serializers.IntegerField(default=10, required=False)
    umbral_retardo_min = serializers.IntegerField(default=5, required=False)


class SesionSerializer(serializers.ModelSerializer):
    fin = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Sesion
        fields = "__all__"
        read_only_fields = ("id", "inicio", "estado")
