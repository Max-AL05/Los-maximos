from decimal import Decimal
from django.db import transaction
from django.db.models import Sum
from .models import Ponderacion

class PonderacionService:
    @staticmethod
    def validar_y_actualizar_rubrica(materia_id, items):
        """
        Valida que la suma sea 100% y realiza el upsert atómico de la rúbrica
        """
        try:
            total_suma = sum(Decimal(str(item.get("porcentaje", 0))) for item in items)
        except (ValueError, TypeError, Decimal.InvalidOperation):
            return False, "Formato de porcentaje inválido."

        if total_suma != Decimal("100.00"):
            return False, f"La suma de los criterios debe ser exactamente 100%. Recibido: {total_suma}%."

        try:
            with transaction.atomic():
                # Limpieza y recreación de la rúbrica 
                Ponderacion.objects.filter(materia_id=materia_id).delete()
                
                nuevas_ponderaciones = [
                    Ponderacion(
                        materia_id=materia_id,
                        nombre=item.get("nombre"),
                        porcentaje=Decimal(str(item.get("porcentaje")))
                    ) for item in items
                ]
                Ponderacion.objects.bulk_create(nuevas_ponderaciones)
            return True, "Rúbrica actualizada correctamente."
        except Exception as e:
            return False, str(e)