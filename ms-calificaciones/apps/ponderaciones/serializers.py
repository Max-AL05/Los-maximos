from rest_framework import serializers
from django.db.models import Sum
from decimal import Decimal, ROUND_HALF_UP
from .models import Ponderacion

class PonderacionSerializer(serializers.ModelSerializer):
    """
    Serializador para la gestión de rúbricas (ponderaciones) de evaluación.
    Garantiza que la suma de criterios por materia sea exactamente 100%.
    """
    class Meta:
        model = Ponderacion
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, data):
        """
        Valida que la suma de porcentajes para la materia no exceda el 100%.
        Requisito: Gestión de ponderaciones (criterios 100%).
        """
        # Obtenemos el materia_id de los datos entrantes o de la instancia existente (en caso de PUT/PATCH)
        materia_id = data.get('materia_id') or (self.instance.materia_id if self.instance else None)
        nuevo_porcentaje = data.get('porcentaje', Decimal('0.00'))

        # Calculamos la suma actual de las ponderaciones ya registradas para esta materia
        # Excluimos el registro actual si estamos editando para no sumarlo dos veces
        query_ponderaciones = Ponderacion.objects.filter(materia_id=materia_id)
        if self.instance:
            query_ponderaciones = query_ponderaciones.exclude(id=self.instance.id)
        
        suma_actual = query_ponderaciones.aggregate(Sum('porcentaje'))['porcentaje__sum'] or Decimal('0.00')

        if suma_actual + nuevo_porcentaje > Decimal('100.00'):
            raise serializers.ValidationError({
                "porcentaje": f"La suma total de ponderaciones para la materia {materia_id} no puede exceder el 100%. "
                              f"Suma actual: {suma_actual}%. Intento de añadir: {nuevo_porcentaje}%."
            })
        
        return data


class ConcentradoAlumnoSerializer(serializers.Serializer):
    """
    Serializador especializado para el Concentrado de Calificaciones.
    Calcula el promedio ponderado, aplica el redondeo institucional y clasifica el estatus.
    """
    alumno_id = serializers.CharField()
    nombre_alumno = serializers.CharField(required=False, default="Cargando...") # Se llena vía gRPC desde MS-3
    promedio_real = serializers.DecimalField(max_digits=5, decimal_places=2)
    promedio_redondeado = serializers.IntegerField(read_only=True)
    estatus = serializers.CharField(read_only=True) # APROBADO, EN RIESGO, REPROBADO
    entregas = serializers.DictField(
        child=serializers.DecimalField(max_digits=5, decimal_places=2),
        help_text="Diccionario mapeando {nombre_actividad: calificacion_obtenida}"
    )

    def to_representation(self, instance):
        """
        Aplica la lógica de negocio institucional al generar la respuesta JSON.
        """
        data = super().to_representation(instance)
        
        # Convertimos a Decimal para asegurar precisión matemática en el cálculo
        promedio_real = Decimal(str(data['promedio_real']))
        
        # Regla institucional: >= 0.5 redondea al entero superior; < 0.5 al inferior 
        redondeado = int(promedio_real.quantize(Decimal('1'), rounding=ROUND_HALF_UP))
        data['promedio_redondeado'] = redondeado
        
        # Clasificación del alumno para el reporte visual 
        if redondeado >= 8:
            data['estatus'] = "APROBADO"
        elif 6 <= redondeado < 8:
            data['estatus'] = "EN RIESGO"
        else:
            data['estatus'] = "REPROBADO"
            
        return data