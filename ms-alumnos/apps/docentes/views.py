"""
Views REST de Docentes.

Endpoints:
    GET  /docentes
    GET  /docentes/<id>
    POST /docentes/importar      (sube PDF directorio institucional)
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .models import Docente
from .serializers import DocenteSerializer, ImportarDocentesSerializer


class DocenteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Docente.objects.all()
    serializer_class = DocenteSerializer

    @action(detail=False, methods=["post"], parser_classes=[MultiPartParser], url_path="importar")
    def importar(self, request):
        """Importa el directorio docente desde PDF institucional."""
        serializer = ImportarDocentesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # TODO: parsear PDF, extraer nombre/correo/cubículo,
        #       crear Docente y luego pedir a MS-1 (gRPC) crear credencial.
        return Response(
            {"success": True, "data": {"importados": 0}, "message": "TODO"},
            status=status.HTTP_201_CREATED,
        )
