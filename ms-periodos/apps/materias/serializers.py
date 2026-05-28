from rest_framework import serializers
from .models import Materia


class MateriaSerializer(serializers.ModelSerializer):
    periodo_nombre = serializers.CharField(source="periodo.nombre", read_only=True)

    class Meta:
        model = Materia
        fields = [
            "id",
            "periodo",
            "periodo_nombre",
            "nrc",
            "nombre",
            "seccion",
            "clave",
            "horario",
            "docente_id",
            "estado",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("id", "periodo_nombre", "created_at", "updated_at")