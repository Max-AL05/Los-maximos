"""
Views REST de Docentes.

Endpoints:
    GET  /docentes
    GET  /docentes/<id>
    POST /docentes/importar      (sube PDF directorio institucional)
"""
import re
import secrets
import string

import pdfplumber
import requests
from django.conf import settings
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Docente
from .serializers import DocenteSerializer, ImportarDocentesSerializer


def _generar_clave_unica(longitud: int = 10) -> str:
    alfabeto = string.ascii_letters + string.digits
    return "".join(secrets.choice(alfabeto) for _ in range(longitud))


def _crear_credencial_ms1(correo: str, nombre_completo: str, clave: str):
    """Crea el usuario DOCENTE en MS-1 y devuelve su user_id."""
    try:
        url = "http://ms-auth:8001/auth/register"
        if hasattr(settings, "REST_URL_AUTH"):
            url = f"{settings.REST_URL_AUTH}/auth/register"
        resp = requests.post(
            url,
            json={
                "email":           correo,
                "password":        clave,
                "role":            "DOCENTE",
                "nombre_completo": nombre_completo,
            },
            timeout=10,
        )
        if resp.status_code in (200, 201):
            return resp.json().get("data", {}).get("id")
    except Exception:
        pass
    return None


def _parsear_pdf_directorio(archivo):
    """
    Parsea el PDF del directorio institucional.
    Estrategia tolerante: busca filas con un patrón email + texto adyacente.
    Devuelve lista de dicts: { nombre_completo, correo, cubiculo }.
    """
    docentes = []
    errores = []
    correo_re = re.compile(r"[\w\.\-]+@[\w\.\-]+\.\w+")

    with pdfplumber.open(archivo) as pdf:
        for num_pag, pagina in enumerate(pdf.pages, start=1):
            # Primero intentar extract_table; si no hay tabla, caer a texto plano
            tabla = pagina.extract_table()
            if tabla:
                for fila in tabla[1:]:  # Saltar encabezado
                    if not fila:
                        continue
                    valores = [str(c).strip() if c else "" for c in fila]
                    # Buscar el correo en la fila
                    correo = next((v for v in valores if correo_re.search(v)), None)
                    if not correo:
                        continue
                    correo = correo_re.search(correo).group(0)
                    # El nombre suele ser la columna previa al correo, el cubículo la siguiente
                    nombre   = valores[0] if valores else ""
                    cubiculo = ""
                    for i, v in enumerate(valores):
                        if correo_re.search(v):
                            if i + 1 < len(valores):
                                cubiculo = valores[i + 1]
                            break
                    if nombre and correo:
                        docentes.append({
                            "nombre_completo": nombre,
                            "correo":          correo,
                            "cubiculo":        cubiculo,
                        })
            else:
                texto = pagina.extract_text() or ""
                for linea in texto.split("\n"):
                    m = correo_re.search(linea)
                    if not m:
                        continue
                    correo = m.group(0)
                    # El nombre es lo que está antes del correo en esa línea
                    nombre = linea[:m.start()].strip()
                    if nombre and correo:
                        docentes.append({
                            "nombre_completo": nombre,
                            "correo":          correo,
                            "cubiculo":        "",
                        })

    return docentes, errores


class DocenteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Docente.objects.all()
    serializer_class = DocenteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(nombre_completo__icontains=q) | qs.filter(correo__icontains=q)
        return qs

    @action(detail=False, methods=["post"], parser_classes=[MultiPartParser], url_path="importar")
    def importar(self, request):
        """POST /docentes/importar — sube PDF del directorio institucional."""
        serializer = ImportarDocentesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        archivo = serializer.validated_data["archivo_pdf"]

        try:
            docentes_raw, errores = _parsear_pdf_directorio(archivo)
        except Exception as exc:
            return Response(
                {"success": False, "data": None, "message": f"Error al leer el PDF: {str(exc)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        creados = 0
        existentes = 0
        with transaction.atomic():
            for d in docentes_raw:
                docente, created = Docente.objects.get_or_create(
                    correo=d["correo"],
                    defaults={
                        "nombre_completo": d["nombre_completo"],
                        "cubiculo":        d["cubiculo"] or None,
                    },
                )
                if created:
                    creados += 1
                    # Crear credencial en MS-1
                    clave = _generar_clave_unica()
                    user_id = _crear_credencial_ms1(
                        correo=docente.correo,
                        nombre_completo=docente.nombre_completo,
                        clave=clave,
                    )
                    if user_id:
                        docente.user_id = user_id
                        docente.save(update_fields=["user_id"])
                else:
                    existentes += 1

        return Response(
            {
                "success": True,
                "data": {
                    "importados":      len(docentes_raw),
                    "docentes_nuevos": creados,
                    "ya_existentes":   existentes,
                    "errores":         errores,
                },
                "message": f"{creados} docentes importados correctamente",
            },
            status=status.HTTP_201_CREATED,
        )