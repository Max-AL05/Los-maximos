from rest_framework import serializers
from .models import Alumno, InscripcionMateria


class AlumnoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alumno
        fields = "__all__"
        read_only_fields = ("id", "user_id", "created_at", "updated_at")


class ImportarAlumnosSerializer(serializers.Serializer):
    archivo_excel = serializers.FileField()


class InscripcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InscripcionMateria
        fields = "__all__"
        read_only_fields = ("id", "fecha_inscripcion", "fecha_baja")
