from rest_framework import serializers
from .models import Actividad, Calificacion


class ActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actividad
        fields = "__all__"
        read_only_fields = ("id", "created_at")


class CalificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calificacion
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ImportarCalificacionesSerializer(serializers.Serializer):
    actividad_id = serializers.UUIDField()
    archivo_excel = serializers.FileField()
