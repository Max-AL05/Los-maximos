"""
Views REST de MS-2 Periodos & Materias.

Endpoints:
    GET    /periodos
    POST   /periodos
    GET    /periodos/<id>
    PUT    /periodos/<id>
    DELETE /periodos/<id>
    POST   /periodos/importar
    GET    /periodos/activo
"""
import pdfplumber
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from .models import Periodo
from apps.materias.models import Materia
from .serializers import PeriodoSerializer, ImportarMateriasSerializer


class PeriodoViewSet(viewsets.ModelViewSet):
    queryset = Periodo.objects.all()
    serializer_class = PeriodoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Si el nuevo periodo se crea como activo, desactiva todos los demás.
        """
        if serializer.validated_data.get("activo", False):
            Periodo.objects.filter(activo=True).update(activo=False)
        serializer.save()

    def perform_update(self, serializer):
        """
        Si se activa un periodo, desactiva el resto.
        """
        if serializer.validated_data.get("activo", False):
            Periodo.objects.exclude(pk=serializer.instance.pk).filter(activo=True).update(activo=False)
        serializer.save()

    @action(detail=False, methods=["get"], url_path="activo")
    def activo(self, request):
        """GET /periodos/activo — devuelve el periodo activo actual."""
        try:
            periodo = Periodo.objects.get(activo=True)
            return Response({
                "success": True,
                "data": PeriodoSerializer(periodo).data,
                "message": "",
            })
        except Periodo.DoesNotExist:
            return Response(
                {"success": False, "data": None, "message": "No hay ningún periodo activo"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=["post"], parser_classes=[MultiPartParser], url_path="importar")
    def importar(self, request):
        """
        POST /periodos/importar
        Sube un PDF de programación académica y extrae las materias.
        Formato esperado en el PDF: filas con NRC, nombre, sección, clave, docente, horario.
        """
        serializer = ImportarMateriasSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        periodo_id = serializer.validated_data["periodo_id"]
        archivo = serializer.validated_data["archivo_pdf"]

        try:
            periodo = Periodo.objects.get(id=periodo_id)
        except Periodo.DoesNotExist:
            return Response(
                {"success": False, "data": None, "message": "Periodo no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        materias_creadas = []
        errores = []

        try:
            with pdfplumber.open(archivo) as pdf:
                for num_pagina, pagina in enumerate(pdf.pages, start=1):
                    tabla = pagina.extract_table()
                    if not tabla:
                        continue

                    # Saltar la fila de encabezados si la primera celda no es un NRC numérico
                    filas = tabla[1:] if tabla and not str(tabla[0][0] or "").strip().isdigit() else tabla

                    for fila in filas:
                        # Limpiar valores None
                        fila = [str(c).strip() if c else "" for c in fila]

                        # Necesitamos al menos 6 columnas: NRC, nombre, sección, clave, docente, horario
                        if len(fila) < 6 or not fila[0].isdigit():
                            continue

                        nrc      = fila[0]
                        nombre   = fila[1]
                        seccion  = fila[2]
                        clave    = fila[3]
                        docente  = fila[4]   # nombre del docente en el PDF
                        horario  = fila[5]

                        if not nrc or not nombre:
                            continue

                        # Crear o actualizar la materia
                        materia, created = Materia.objects.update_or_create(
                            periodo=periodo,
                            nrc=nrc,
                            seccion=seccion,
                            defaults={
                                "nombre":     nombre,
                                "clave":      clave,
                                "horario":    horario,
                                "docente_id": docente,  # se resolverá a UUID vía gRPC MS-3 después
                            },
                        )
                        materias_creadas.append({
                            "nrc":    nrc,
                            "nombre": nombre,
                            "nueva":  created,
                        })

        except Exception as exc:
            return Response(
                {"success": False, "data": None, "message": f"Error al procesar el PDF: {str(exc)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "success": True,
                "data": {
                    "importadas": len(materias_creadas),
                    "materias":   materias_creadas,
                    "errores":    errores,
                },
                "message": f"{len(materias_creadas)} materias importadas correctamente",
            },
            status=status.HTTP_201_CREATED,
        )