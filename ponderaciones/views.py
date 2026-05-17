from decimal import Decimal
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Ponderacion
from .serializers import PonderacionSerializer

@api_view(["GET", "POST", "PUT"])
# @permission_classes([IsAuthenticated])
@permission_classes([AllowAny])
def ponderaciones_view(request, materia_id):
    """
    Maneja la rúbrica de evaluación por materia.
    """
    if request.method == "GET":
        qs = Ponderacion.objects.filter(materia_id=materia_id)
        return Response({
            "success": True, 
            "data": PonderacionSerializer(qs, many=True).data
        })

    # Para POST y PUT esperamos una lista de objetos: [{"nombre": "Exámenes", "porcentaje": 60}, ...]
    data = request.data if isinstance(request.data, list) else request.data.get("items", [])
    
    if not data:
        return Response({"success": False, "message": "No se enviaron datos de ponderación."}, status=400)

    # Validación crítica: La suma debe ser exactamente 100.00
    try:
        total_suma = sum(Decimal(str(item.get("porcentaje", 0))) for item in data)
    except Exception:
        return Response({"success": False, "message": "Formato de porcentaje inválido."}, status=400)

    if total_suma != Decimal("100.00"):
        return Response({
            "success": False, 
            "message": f"La suma de los criterios debe ser exactamente 100%. Recibido: {total_suma}%"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Operación Atómica: Borrar la rúbrica vieja y crear la nueva
    try:
        with transaction.atomic():
            Ponderacion.objects.filter(materia_id=materia_id).delete()
            
            nuevas_ponderaciones = [
                Ponderacion(
                    materia_id=materia_id,
                    nombre=item.get("nombre"),
                    porcentaje=Decimal(str(item.get("porcentaje")))
                ) for item in data
            ]
            Ponderacion.objects.bulk_create(nuevas_ponderaciones)

        return Response({
            "success": True, 
            "message": "Rúbrica de evaluación actualizada correctamente."
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({"success": False, "message": str(e)}, status=500)