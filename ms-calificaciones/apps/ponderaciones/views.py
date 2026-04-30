"""
Endpoints:
    GET  /ponderaciones/<materia_id>
    POST /ponderaciones/<materia_id>     (lista completa, valida suma=100)
    PUT  /ponderaciones/<materia_id>
"""
from decimal import Decimal
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
        qs = Ponderacion.objects.filter(materia_id=materia_id)
        return Response({"success": True, "data": PonderacionSerializer(qs, many=True).data})

    # POST y PUT: la suma debe ser 100
    items = request.data if isinstance(request.data, list) else request.data.get("items", [])
    total = sum(Decimal(str(i.get("porcentaje", 0))) for i in items)
    if total != Decimal("100"):
        return Response(
            {"success": False, "message": f"La suma de porcentajes debe ser 100, recibida: {total}"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    # TODO: borrar existentes y re-crear, o hacer upsert
    return Response({"success": True, "message": "TODO"}, status=status.HTTP_200_OK)
