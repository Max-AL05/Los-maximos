from rest_framework import serializers
from .models import Periodo


class PeriodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periodo
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ImportarMateriasSerializer(serializers.Serializer):
    periodo_id = serializers.UUIDField()
    archivo_pdf = serializers.FileField()
