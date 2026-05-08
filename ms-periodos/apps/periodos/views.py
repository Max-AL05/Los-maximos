from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny  # TODO: cambiar a IsAuthenticated cuando MS-1 esté listo

from .models import Periodo
from .serializers import PeriodoSerializer, ImportarMateriasSerializer


class PeriodoViewSet(viewsets.ModelViewSet):
    queryset = Periodo.objects.all()
    serializer_class = PeriodoSerializer
    permission_classes = [AllowAny]  # TODO: reemplazar por IsAuthenticated + RBAC Admin

    @transaction.atomic
    def perform_create(self, serializer):
        if serializer.validated_data.get("activo"):
            Periodo.objects.filter(activo=True).update(activo=False)
        serializer.save()

    @transaction.atomic
    def perform_update(self, serializer):
        if serializer.validated_data.get("activo"):
            Periodo.objects.filter(activo=True).exclude(pk=serializer.instance.pk).update(activo=False)
        serializer.save()

    @action(detail=True, methods=["post"], url_path="activar")
    @transaction.atomic
    def activar(self, request, pk=None):
        periodo = self.get_object()
        Periodo.objects.filter(activo=True).exclude(pk=periodo.pk).update(activo=False)
        periodo.activo = True
        periodo.save(update_fields=["activo", "updated_at"])
        return Response(
            {"success": True, "data": PeriodoSerializer(periodo).data, "message": "Periodo activado"},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="activo")
    def activo(self, request):
        periodo = Periodo.objects.filter(activo=True).first()
        if not periodo:
            return Response(
                {"success": False, "data": None, "message": "No hay periodo activo"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"success": True, "data": PeriodoSerializer(periodo).data, "message": "OK"},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], parser_classes=[MultiPartParser], url_path="importar")
    def importar(self, request):
        serializer = ImportarMateriasSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # TODO: parsear PDF con pdfplumber, extraer NRC/nombre/sección/docente/horario,
        #       crear Materia por cada fila. Antes de crear cada Materia, llamar gRPC
        #       a MS-3 para resolver docente_id desde su nombre/correo.
        return Response(
            {"success": True, "data": {"importadas": 0}, "message": "Pendiente de implementar"},
            status=status.HTTP_201_CREATED,
        )