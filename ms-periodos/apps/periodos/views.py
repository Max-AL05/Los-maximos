import re
from collections import defaultdict

import pdfplumber
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny

from apps.materias.models import Materia
from .models import Periodo
from .serializers import PeriodoSerializer, ImportarMateriasSerializer


class PeriodoViewSet(viewsets.ModelViewSet):
    queryset = Periodo.objects.all()
    serializer_class = PeriodoSerializer
    permission_classes = [AllowAny]

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
    @transaction.atomic
    def importar(self, request):
        serializer = ImportarMateriasSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        periodo_id  = serializer.validated_data["periodo_id"]
        archivo_pdf = serializer.validated_data["archivo_pdf"]

        try:
            periodo = Periodo.objects.get(pk=periodo_id)
        except Periodo.DoesNotExist:
            return Response(
                {"success": False, "data": None, "message": "Periodo no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        filas = _parsear_pdf(archivo_pdf)
        importadas, omitidas = _crear_materias(filas, periodo)

        return Response(
            {
                "success": True,
                "data": {"importadas": importadas, "omitidas": omitidas},
                "message": f"{importadas} materias importadas, {omitidas} omitidas (duplicadas).",
            },
            status=status.HTTP_201_CREATED,
        )


# ─────────────────────────────────────────────
# Helpers de parseo
# ─────────────────────────────────────────────

def _parsear_pdf(archivo) -> list[dict]:
    """
    Extrae filas del PDF de programación académica BUAP.
    Formato esperado por columna:
      NRC | Clave | Materia | Secc | Dias | Hora | Profesor | Salon
    Cada NRC aparece varias veces (una por día). Se agrupa por NRC+Secc
    y se concatena el horario.
    """
    grupos: dict[tuple, dict] = {}

    with pdfplumber.open(archivo) as pdf:
        for page in pdf.pages:
            tabla = page.extract_table()
            if not tabla:
                # intenta con texto plano si no hay tabla estructurada
                for linea in (page.extract_text() or "").splitlines():
                    fila = _parsear_linea(linea)
                    if fila:
                        _acumular(grupos, fila)
                continue

            for row in tabla:
                if not row or not row[0]:
                    continue
                nrc_raw = str(row[0]).strip()
                if not nrc_raw.isdigit():
                    continue  # cabecera u otras líneas
                fila = {
                    "nrc":      nrc_raw,
                    "clave":    str(row[1] or "").strip(),
                    "nombre":   str(row[2] or "").strip(),
                    "seccion":  str(row[3] or "").strip(),
                    "dias":     str(row[4] or "").strip(),
                    "hora":     str(row[5] or "").strip(),
                    "docente":  str(row[6] or "").strip(),
                    "salon":    str(row[7] or "").strip(),
                }
                _acumular(grupos, fila)

    return list(grupos.values())


def _parsear_linea(linea: str) -> dict | None:
    """Fallback: parsea una línea de texto plano con regex."""
    # Ejemplo: 50030 CCOS 260 Redes de Computadoras OO1 L 1000-1059 TREVINO - SANCHEZ DANIEL 1CCO4/305
    m = re.match(
        r"^(\d{5})\s+"          # NRC
        r"([A-Z]{4}\s+\d{3})\s+" # Clave
        r"(.+?)\s+"              # Nombre materia
        r"([A-Z0-9]{3})\s+"      # Sección
        r"([LMAJVS]+)\s+"        # Días
        r"(\d{4}-\d{4})\s+"      # Hora
        r"(.+?)\s+"              # Docente
        r"(\S+)$",               # Salón
        linea.strip(),
    )
    if not m:
        return None
    return {
        "nrc":     m.group(1),
        "clave":   m.group(2).replace(" ", ""),
        "nombre":  m.group(3).strip(),
        "seccion": m.group(4),
        "dias":    m.group(5),
        "hora":    m.group(6),
        "docente": m.group(7).strip(),
        "salon":   m.group(8),
    }


def _acumular(grupos: dict, fila: dict):
    """Agrupa filas del mismo NRC+sección sumando días."""
    key = (fila["nrc"], fila["seccion"])
    if key not in grupos:
        grupos[key] = {**fila, "horario": f"{fila['dias']} {fila['hora']}"}
    else:
        # agrega el día si no está ya
        existente = grupos[key]["horario"]
        nuevo_dia = f"{fila['dias']} {fila['hora']}"
        if nuevo_dia not in existente:
            grupos[key]["horario"] += f" / {nuevo_dia}"


def _crear_materias(filas: list[dict], periodo: Periodo) -> tuple[int, int]:
    importadas = 0
    omitidas   = 0

    for f in filas:
        # Normaliza clave: "CCOS 260" → "CCOS260"
        clave_norm = re.sub(r"\s+", "", f.get("clave", ""))

        # docente_id: guardamos el nombre normalizado como identificador
        # (sin integración gRPC a MS-3 en esta versión)
        docente_id = _normalizar_nombre(f.get("docente", ""))

        existe = Materia.objects.filter(
            periodo=periodo,
            nrc=f["nrc"],
            seccion=f["seccion"],
        ).exists()

        if existe:
            omitidas += 1
            continue

        Materia.objects.create(
            periodo=periodo,
            nrc=f["nrc"],
            nombre=f.get("nombre", ""),
            seccion=f.get("seccion", ""),
            clave=clave_norm,
            horario=f.get("horario", ""),
            docente_id=docente_id,
            estado="ABIERTA",
        )
        importadas += 1

    return importadas, omitidas


def _normalizar_nombre(nombre: str) -> str:
    """TREVINO - SANCHEZ DANIEL  →  TREVINO SANCHEZ DANIEL"""
    return re.sub(r"\s*-\s*", " ", nombre).strip()