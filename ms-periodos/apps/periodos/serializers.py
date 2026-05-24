from rest_framework import serializers
from .models import Periodo


class PeriodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periodo
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        fecha_inicio = attrs.get("fecha_inicio", getattr(self.instance, "fecha_inicio", None))
        fecha_fin = attrs.get("fecha_fin", getattr(self.instance, "fecha_fin", None))

        if fecha_inicio and fecha_fin and fecha_fin <= fecha_inicio:
            raise serializers.ValidationError(
                {"fecha_fin": "La fecha fin debe ser posterior a la fecha de inicio."}
            )
        return attrs


class ImportarMateriasSerializer(serializers.Serializer):
    periodo_id = serializers.UUIDField()
    archivo_pdf = serializers.FileField()