"""
Endpoints de Actividades y Calificaciones:
    GET/POST/PUT/DELETE /actividades/          (ViewSet)
    GET/POST/PUT/DELETE /calificaciones/       (ViewSet)
    POST                /calificaciones/importar  (Excel masivo)
    GET                 /concentrado/<materia_id> (promedios ponderados)
"""
import io
from decimal import Decimal, ROUND_HALF_UP

import openpyxl
from django.conf import settings
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Actividad, Calificacion
from .serializers import (
    ActividadSerializer,
    CalificacionSerializer,
    ImportarCalificacionesSerializer,
)
from apps.ponderaciones.models import Ponderacion


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _redondear_institucional(valor: Decimal) -> int:
    """
    Regla de redondeo BUAP:
        fracción >= 0.5 → al entero superior
        fracción <  0.5 → al entero inferior
    """
    entero = int(valor)
    fraccion = valor - entero
    return entero + 1 if fraccion >= Decimal("0.5") else entero


def _get_alumnos_materia(materia_id: str) -> list[dict]:
    """
    Llama a MS-3 vía gRPC para obtener los alumnos inscritos en la materia.
    Devuelve lista de dicts con alumno_id, matricula, nombre_completo.
    """
    try:
        import grpc
        from protos import alumnos_pb2, alumnos_pb2_grpc
        target = settings.GRPC_TARGETS["alumnos"]
        with grpc.insecure_channel(target) as channel:
            stub = alumnos_pb2_grpc.AlumnosServiceStub(channel)
            resp = stub.GetAlumnosByMateria(
                alumnos_pb2.GetAlumnosByMateriaRequest(materia_id=materia_id)
            )
            return [
                {
                    "alumno_id":       a.alumno_id,
                    "matricula":       a.matricula,
                    "nombre_completo": a.nombre_completo,
                }
                for a in resp.alumnos
            ]
    except Exception:
        return []


def _calcular_concentrado(materia_id: str) -> list[dict]:
    """
    Calcula el promedio ponderado real y redondeado para cada alumno.

    Algoritmo:
        1. Para cada ponderación de la materia, obtener las actividades y sus calificaciones.
        2. Calcular el promedio del alumno en esa categoría.
        3. Aplicar el peso: promedio_categoria * (porcentaje / 100).
        4. Sumar para obtener el promedio ponderado final.
        5. Redondear con la regla institucional.
    """
    alumnos = _get_alumnos_materia(materia_id)
    ponderaciones = list(Ponderacion.objects.filter(materia_id=materia_id).prefetch_related("actividades"))

    resultado = []
    for alumno in alumnos:
        alumno_id = alumno["alumno_id"]
        promedio_ponderado = Decimal("0")

        for pond in ponderaciones:
            actividades = list(pond.actividades.all())
            if not actividades:
                continue

            califs = Calificacion.objects.filter(
                actividad__in=actividades,
                alumno_id=alumno_id,
            ).values_list("actividad_id", "valor")

            califs_dict = {str(a): v for a, v in califs}

            # Promedio de la categoría
            valores = []
            for act in actividades:
                v = califs_dict.get(str(act.id))
                if v is not None:
                    # Normalizar a escala 0-10
                    normalizado = (Decimal(str(v)) / Decimal(str(act.valor_maximo))) * Decimal("10")
                    valores.append(normalizado)
                else:
                    valores.append(Decimal("0"))

            promedio_cat = sum(valores) / len(valores) if valores else Decimal("0")
            promedio_ponderado += promedio_cat * (Decimal(str(pond.porcentaje)) / Decimal("100"))

        redondeado = _redondear_institucional(promedio_ponderado)
        resultado.append({
            "alumno_id":          alumno_id,
            "matricula":          alumno["matricula"],
            "nombre_completo":    alumno["nombre_completo"],
            "promedio_real":      float(round(promedio_ponderado, 2)),
            "promedio_redondeado": redondeado,
            "estado": "APROBADO" if redondeado >= 6 else "REPROBADO",
        })

    return resultado


# ---------------------------------------------------------------------------
# ViewSets
# ---------------------------------------------------------------------------
class ActividadViewSet(viewsets.ModelViewSet):
    serializer_class = ActividadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Actividad.objects.all()
        materia_id = self.request.query_params.get("materia_id")
        if materia_id:
            qs = qs.filter(ponderacion__materia_id=materia_id)
        ponderacion_id = self.request.query_params.get("ponderacion_id")
        if ponderacion_id:
            qs = qs.filter(ponderacion_id=ponderacion_id)
        return qs.select_related("ponderacion")

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        data = ActividadSerializer(qs, many=True).data
        return Response({"success": True, "data": data, "message": ""})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {"success": True, "data": serializer.data, "message": "Actividad creada"},
            status=status.HTTP_201_CREATED,
        )


class CalificacionViewSet(viewsets.ModelViewSet):
    serializer_class = CalificacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Calificacion.objects.all()
        alumno_id    = self.request.query_params.get("alumno_id")
        actividad_id = self.request.query_params.get("actividad_id")
        materia_id   = self.request.query_params.get("materia_id")
        if alumno_id:
            qs = qs.filter(alumno_id=alumno_id)
        if actividad_id:
            qs = qs.filter(actividad_id=actividad_id)
        if materia_id:
            qs = qs.filter(actividad__ponderacion__materia_id=materia_id)
        return qs.select_related("actividad__ponderacion")

    def create(self, request, *args, **kwargs):
        """Upsert: si ya existe la combinación (actividad, alumno), actualiza."""
        actividad_id = request.data.get("actividad")
        alumno_id    = request.data.get("alumno_id")
        valor        = request.data.get("valor")

        if not all([actividad_id, alumno_id, valor is not None]):
            return Response(
                {"success": False, "data": None,
                 "message": "Faltan campos: actividad, alumno_id, valor"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        calif, created = Calificacion.objects.update_or_create(
            actividad_id=actividad_id,
            alumno_id=alumno_id,
            defaults={"valor": Decimal(str(valor))},
        )
        return Response(
            {
                "success": True,
                "data": CalificacionSerializer(calif).data,
                "message": "Calificación guardada",
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# Importar calificaciones desde Excel
# ---------------------------------------------------------------------------
@api_view(["POST"])
@parser_classes([MultiPartParser])
@permission_classes([IsAuthenticated])
def importar_calificaciones(request):
    """
    POST /calificaciones/importar
    Body multipart:
        - actividad_id: UUID
        - archivo_excel: .xlsx
    Formato del Excel: columna A = alumno_id (UUID), columna B = calificación (0-10)
    """
    serializer = ImportarCalificacionesSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    actividad_id = serializer.validated_data["actividad_id"]
    archivo      = serializer.validated_data["archivo_excel"]

    try:
        actividad = Actividad.objects.get(id=actividad_id)
    except Actividad.DoesNotExist:
        return Response(
            {"success": False, "data": None, "message": "Actividad no encontrada"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        wb = openpyxl.load_workbook(io.BytesIO(archivo.read()), data_only=True)
        ws = wb.active
    except Exception as exc:
        return Response(
            {"success": False, "data": None, "message": f"No se pudo leer el Excel: {exc}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    importadas = 0
    errores    = []

    with transaction.atomic():
        for idx, fila in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            if not fila or all(c is None for c in fila):
                continue
            alumno_id = str(fila[0]).strip() if fila[0] else ""
            try:
                valor = Decimal(str(fila[1])).quantize(Decimal("0.01"))
            except Exception:
                errores.append({"fila": idx, "error": "Calificación inválida"})
                continue

            if not alumno_id:
                errores.append({"fila": idx, "error": "alumno_id vacío"})
                continue

            if valor < 0 or valor > actividad.valor_maximo:
                errores.append({
                    "fila": idx,
                    "error": f"Valor fuera de rango (0-{actividad.valor_maximo})",
                })
                continue

            Calificacion.objects.update_or_create(
                actividad=actividad,
                alumno_id=alumno_id,
                defaults={"valor": valor},
            )
            importadas += 1

    return Response(
        {
            "success": True,
            "data": {"importadas": importadas, "errores": errores},
            "message": f"{importadas} calificaciones importadas",
        },
        status=status.HTTP_200_OK,
    )


# ---------------------------------------------------------------------------
# Concentrado
# ---------------------------------------------------------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def concentrado(request, materia_id):
    """
    GET /concentrado/<materia_id>
    Devuelve el concentrado de calificaciones con promedio ponderado real y redondeado.
    """
    try:
        data = _calcular_concentrado(str(materia_id))
        return Response({
            "success": True,
            "data": data,
            "message": "",
        })
    except Exception as exc:
        return Response(
            {"success": False, "data": None, "message": f"Error al calcular el concentrado: {exc}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )