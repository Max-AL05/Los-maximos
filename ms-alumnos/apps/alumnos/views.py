"""
Views REST de Alumnos.

Endpoints:
    POST   /alumnos/importar/<materia_id>      (Excel/CSV con vista previa)
    GET    /alumnos/materia/<materia_id>
    DELETE /alumnos/<id>/baja                  (irreversible, notifica a docente)
"""
import unicodedata
import pandas as pd
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Alumno, InscripcionMateria
from .serializers import (
    AlumnoSerializer,
    ImportarAlumnosSerializer,
)


def normalizar(texto):
    """Quita tildes y convierte a minúsculas."""
    return unicodedata.normalize('NFKD', str(texto)).encode('ascii', 'ignore').decode('ascii').lower().strip()


@api_view(["POST"])
@parser_classes([MultiPartParser])
@permission_classes([])
def importar_alumnos(request, materia_id):
    """POST /alumnos/importar/<materia_id> – Excel/CSV con vista previa."""
    serializer = ImportarAlumnosSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    archivo = serializer.validated_data["archivo_excel"]
    preview = request.query_params.get("preview", "false").lower() == "true"

    try:
       df = pd.read_excel(archivo, sheet_name="Asistencias", header=5)
       print("COLUMNAS:", df.columns.tolist())
    except Exception:
        return Response(
            {"success": False, "message": "Archivo inválido, sube un Excel válido."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Normalizar columnas - quitar tildes y espacios
    df.columns = [normalizar(c) for c in df.columns]

    # Validar columnas requeridas
    columnas_requeridas = {"matricula", "nombre"}
    if not columnas_requeridas.issubset(set(df.columns)):
        return Response(
            {
                "success": False,
                "message": f"Columnas encontradas: {list(df.columns[:5])}",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    alumnos_preview = []
    errores = []

    for i, row in df.iterrows():
        matricula = str(row["matricula"]).strip()
        nombre = str(row["nombre"]).strip()

        # Saltar filas vacías o inválidas
        if not matricula or not nombre or matricula == "nan" or nombre == "nan":
            errores.append({"fila": i + 2, "error": "Campos vacíos"})
            continue

        # Generar correo automático desde matrícula
        correo = f"{matricula.lower()}@alumno.buap.mx"

        alumnos_preview.append({
            "matricula": matricula,
            "nombre_completo": nombre,
            "correo": correo,
        })

    # Si es preview, solo devuelve la lista sin guardar
    if preview:
        return Response({
            "success": True,
            "data": {"preview": alumnos_preview, "errores": errores},
            "message": f"{len(alumnos_preview)} alumnos listos para importar.",
        })

    # Si no es preview, guarda en BD
    importados = 0
    for alumno_data in alumnos_preview:
        alumno, creado = Alumno.objects.get_or_create(
            matricula=alumno_data["matricula"],
            defaults={
                "nombre_completo": alumno_data["nombre_completo"],
                "correo": alumno_data["correo"],
            },
        )
        InscripcionMateria.objects.get_or_create(
            alumno=alumno,
            materia_id=str(materia_id),
        )
        if creado:
            importados += 1

    return Response(
        {
            "success": True,
            "data": {"importados": importados, "errores": errores},
            "message": f"{importados} alumnos importados correctamente.",
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def alumnos_por_materia(request, materia_id):
    """GET /alumnos/materia/<materia_id>"""
    inscripciones = InscripcionMateria.objects.filter(
        materia_id=materia_id, dado_de_baja=False
    ).select_related("alumno")
    data = AlumnoSerializer([i.alumno for i in inscripciones], many=True).data
    return Response({"success": True, "data": data, "message": ""})


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def baja_alumno(request, alumno_id):
    """DELETE /alumnos/<alumno_id>/baja – baja irreversible."""
    materia_id = request.data.get("materia_id") or request.query_params.get("materia_id")

    if not materia_id:
        return Response(
            {"success": False, "message": "Se requiere materia_id."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        inscripcion = InscripcionMateria.objects.get(
            alumno_id=alumno_id,
            materia_id=materia_id,
            dado_de_baja=False,
        )
    except InscripcionMateria.DoesNotExist:
        return Response(
            {"success": False, "message": "Inscripción no encontrada o ya fue dada de baja."},
            status=status.HTTP_404_NOT_FOUND,
        )

    inscripcion.dado_de_baja = True
    inscripcion.fecha_baja = timezone.now()
    inscripcion.save()

    return Response(
        {"success": True, "message": "Alumno dado de baja correctamente."},
        status=status.HTTP_200_OK,
    )