"""
Endpoints de Ponderaciones:
    GET  /ponderaciones/<materia_id>    → lista las categorías
    POST /ponderaciones/<materia_id>    → guarda la configuración completa (valida suma=100)
    PUT  /ponderaciones/<materia_id>    → igual que POST (idempotente)
"""
from decimal import Decimal

from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Ponderacion
from .serializers import PonderacionSerializer


@api_view(["GET", "POST", "PUT"])
@permission_classes([IsAuthenticated])
def ponderaciones_view(request, materia_id):

    if request.method == "GET":
        qs = Ponderacion.objects.filter(materia_id=str(materia_id)).order_by("nombre")
        return Response({
            "success": True,
            "data": PonderacionSerializer(qs, many=True).data,
            "message": "",
        })

    # POST / PUT — recibir lista de { nombre, porcentaje }
    items = request.data if isinstance(request.data, list) else request.data.get("items", [])

    if not items:
        return Response(
            {"success": False, "data": None, "message": "Debes enviar al menos una ponderación"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validar suma == 100
    try:
        total = sum(Decimal(str(i.get("porcentaje", 0))) for i in items)
    except Exception:
        return Response(
            {"success": False, "data": None, "message": "Porcentajes inválidos"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if total != Decimal("100"):
        return Response(
            {
                "success": False,
                "data": None,
                "message": f"La suma de porcentajes debe ser exactamente 100. Actual: {total}",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validar que cada item tenga nombre y porcentaje
    for i, item in enumerate(items):
        if not item.get("nombre"):
            return Response(
                {"success": False, "data": None, "message": f"El item {i+1} no tiene nombre"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if Decimal(str(item.get("porcentaje", 0))) <= 0:
            return Response(
                {"success": False, "data": None,
                 "message": f"El porcentaje del item '{item.get('nombre')}' debe ser mayor a 0"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    # Upsert: borrar existentes y re-crear dentro de una transacción
    with transaction.atomic():
        Ponderacion.objects.filter(materia_id=str(materia_id)).delete()
        nuevas = [
            Ponderacion(
                materia_id=str(materia_id),
                nombre=item["nombre"],
                porcentaje=Decimal(str(item["porcentaje"])),
            )
            for item in items
        ]
        Ponderacion.objects.bulk_create(nuevas)

    qs = Ponderacion.objects.filter(materia_id=str(materia_id)).order_by("nombre")
    return Response(
        {
            "success": True,
            "data": PonderacionSerializer(qs, many=True).data,
            "message": "Ponderaciones guardadas correctamente",
        },
        status=status.HTTP_200_OK,
    )
