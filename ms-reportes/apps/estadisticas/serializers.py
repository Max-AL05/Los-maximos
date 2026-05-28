from rest_framework import serializers
from .models import EstadisticaPeriodo


class EstadisticaPeriodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadisticaPeriodo
        fields = "__all__"
