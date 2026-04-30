"""
Views REST de Materias.

Endpoints:
    GET /materias?periodo=:id
    GET /materias/<id>
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Materia
from .serializers import MateriaSerializer


class MateriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Materia.objects.select_related("periodo").all()
    serializer_class = MateriaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        periodo_id = self.request.query_params.get("periodo")
        if periodo_id:
            qs = qs.filter(periodo_id=periodo_id)
        return qs
