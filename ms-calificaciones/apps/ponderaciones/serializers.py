from rest_framework import serializers
from .models import Ponderacion


class PonderacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ponderacion
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
