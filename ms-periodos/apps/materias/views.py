from rest_framework import viewsets
from rest_framework.permissions import AllowAny 
from .models import Materia
from .serializers import MateriaSerializer


class MateriaViewSet(viewsets.ModelViewSet):
    queryset = Materia.objects.select_related("periodo").all()
    serializer_class = MateriaSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params

        periodo_id = params.get("periodo")
        if periodo_id:
            qs = qs.filter(periodo_id=periodo_id)

        docente_id = params.get("docente_id")
        if docente_id:
            qs = qs.filter(docente_id=docente_id)

        estado = params.get("estado")
        if estado:
            qs = qs.filter(estado=estado)

        return qs