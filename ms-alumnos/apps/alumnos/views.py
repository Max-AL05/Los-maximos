"""
Views REST de Alumnos.

Endpoints:
    POST   /alumnos/importar/<materia_id>      (Excel/CSV con vista previa)
    GET    /alumnos/materia/<materia_id>
    DELETE /alumnos/<id>/baja                  (irreversible, notifica a docente)
"""
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


@api_view(["POST"])
@parser_classes([MultiPartParser])
@permission_classes([IsAuthenticated])
def importar_alumnos(request, materia_id):
    """POST /alumnos/importar/<materia_id> – Excel/CSV con vista previa."""
    serializer = ImportarAlumnosSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    # TODO:
    # 1. Parsear Excel con openpyxl/pandas
    # 2. Validar duplicados, formato de matrícula, correo
    # 3. Si "preview" → devolver lista sin guardar
    # 4. Si "confirm" → crear Alumno + InscripcionMateria
    # 5. Para cada alumno NUEVO (sin user_id) → llamar gRPC a MS-1 para crear credencial
    # 6. Llamar gRPC a MS-6 SendBienvenida con la clave única
    return Response(
        {"success": True, "data": {"importados": 0, "preview": []}, "message": "TODO"},
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
    # TODO:
    # 1. Validar que el request.user es ese alumno
    # 2. Verificar que la materia_id viene en el body o querystring
    # 3. Marcar dado_de_baja=True, fecha_baja=now()
    # 4. Llamar gRPC a MS-6 SendBajaNotif (alumno → docente)
    return Response({"success": True, "message": "TODO"}, status=status.HTTP_200_OK)
