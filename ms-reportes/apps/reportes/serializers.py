from rest_framework import serializers
from .models import ReporteGenerado


class ReporteGeneradoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReporteGenerado
        fields = "__all__"