from rest_framework import serializers
from .models import Materia


class MateriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materia
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
