"""
Views REST de Periodos.

Endpoints:
    GET    /periodos
    POST   /periodos
    GET    /periodos/<id>
    PUT    /periodos/<id>
    DELETE /periodos/<id>
    POST   /periodos/importar     (sube PDF de programación académica)
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from .models import Periodo
from .serializers import PeriodoSerializer, ImportarMateriasSerializer


class PeriodoViewSet(viewsets.ModelViewSet):
    queryset = Periodo.objects.all()
    serializer_class = PeriodoSerializer

    @action(detail=False, methods=["post"], parser_classes=[MultiPartParser], url_path="importar")
    def importar(self, request):
        """Importa materias desde un PDF oficial de programación académica."""
        serializer = ImportarMateriasSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # TODO: parsear PDF con pdfplumber, extraer NRC/nombre/sección/docente/horario,
        #       crear Materia por cada fila. Antes de crear cada Materia, llamar gRPC
        #       a MS-3 para resolver docente_id desde su nombre/correo.
        return Response({"success": True, "data": {"importadas": 0}, "message": "TODO"},
                        status=status.HTTP_201_CREATED)
