from rest_framework import serializers
from .models import Docente


class DocenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Docente
        fields = "__all__"
        read_only_fields = ("id", "user_id", "created_at", "updated_at")


class ImportarDocentesSerializer(serializers.Serializer):
    archivo_pdf = serializers.FileField()
