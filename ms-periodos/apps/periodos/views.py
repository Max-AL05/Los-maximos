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
import grpc
import pdfplumber
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from .models import Periodo
from apps.materias.models import Materia
from .serializers import PeriodoSerializer, ImportarMateriasSerializer


# ---------------------------------------------------------------------------
# Helper: resolver nombre de docente a UUID via gRPC MS-3
# ---------------------------------------------------------------------------
def _resolver_docente_id(nombre_docente: str) -> str:
    """
    Consulta MS-3 vía gRPC para obtener el UUID del docente por nombre.
    Si no lo encuentra o falla, devuelve el nombre original como fallback
    para no perder el dato del PDF.
    """
    try:
        from protos import periodos_pb2, periodos_pb2_grpc
        # MS-3 no expone búsqueda por nombre directamente en el proto,
        # así que buscamos via REST interno como fallback seguro.
        # Por ahora guardamos el nombre — se puede resolver en un proceso posterior
        # cuando MS-3 esté disponible.
        return nombre_docente
    except Exception:
        return nombre_docente


def _buscar_docente_por_nombre(nombre_docente: str) -> str | None:
    """
    Llama a MS-3 vía REST interno para buscar el UUID del docente por nombre completo.
    Devuelve el UUID como string, o None si no se encuentra.
    """
    try:
        import requests
        url = getattr(settings, "REST_URL_ALUMNOS", "http://ms-alumnos:8003")
        resp = requests.get(
            f"{url}/docentes/",
            params={"search": nombre_docente},
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            resultados = data.get("results", data) if isinstance(data, dict) else data
            if isinstance(resultados, list) and resultados:
                # Buscar coincidencia exacta por nombre
                for doc in resultados:
                    if doc.get("nombre_completo", "").strip().lower() == nombre_docente.strip().lower():
                        return str(doc.get("id") or doc.get("docente_id"))
                # Si no hay exacta, devolver el primero
                return str(resultados[0].get("id") or resultados[0].get("docente_id"))
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# ViewSets
# ---------------------------------------------------------------------------
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
        Intenta resolver el nombre del docente a UUID via MS-3.
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
                        nombre_docente = fila[4]
                        horario  = fila[5]

                        if not nrc or not nombre:
                            continue

                        # Intentar resolver el nombre del docente a UUID
                        docente_id = _buscar_docente_por_nombre(nombre_docente)
                        if not docente_id:
                            # Guardar el nombre como fallback — se puede resolver después
                            docente_id = nombre_docente
                            errores.append({
                                "nrc": nrc,
                                "aviso": f"No se pudo resolver UUID del docente '{nombre_docente}', se guardó el nombre",
                            })

                        # Crear o actualizar la materia
                        materia, created = Materia.objects.update_or_create(
                            periodo=periodo,
                            nrc=nrc,
                            seccion=seccion,
                            defaults={
                                "nombre":     nombre,
                                "clave":      clave,
                                "horario":    horario,
                                "docente_id": docente_id,
                            },
                        )
                        materias_creadas.append({
                            "nrc":         nrc,
                            "nombre":      nombre,
                            "docente_id":  docente_id,
                            "nueva":       created,
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
                    "avisos":     errores,
                },
                "message": f"{len(materias_creadas)} materias importadas correctamente",
            },
            status=status.HTTP_201_CREATED,
        )