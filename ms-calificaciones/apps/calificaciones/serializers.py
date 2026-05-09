from rest_framework import serializers
from .models import Actividad, Calificacion
from decimal import Decimal, ROUND_HALF_UP

class ActividadSerializer(serializers.ModelSerializer):
    """
    Serializador para gestionar las tareas o exámenes.
    """
    class Meta:
        model = Actividad
        fields = "__all__"
        read_only_fields = ("id", "created_at")

    def validate_valor_maximo(self, value):
        """Asegura que el valor máximo sea positivo (ej. base 10)."""
        if value <= 0:
            raise serializers.ValidationError("El valor máximo de la actividad debe ser mayor a 0.")
        return value


class CalificacionSerializer(serializers.ModelSerializer):
    """
    Serializador para notas individuales con lógica de estatus y redondeo.
    """
    # Campos calculados que se muestran al consultar, pero no se envían al crear
    valor_redondeado = serializers.SerializerMethodField()
    estatus_rendimiento = serializers.SerializerMethodField()

    class Meta:
        model = Calificacion
        fields = (
            "id", "actividad", "alumno_id", "valor", 
            "valor_redondeado", "estatus_rendimiento", 
            "created_at", "updated_at"
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, data):
        """
        Valida que la calificación no sea mayor al valor máximo permitido 
        por la actividad.
        """
        actividad = data.get('actividad')
        valor = data.get('valor')
        
        if valor > actividad.valor_maximo:
            raise serializers.ValidationError({
                "valor": f"La calificación ({valor}) no puede ser mayor al valor máximo de la actividad ({actividad.valor_maximo})."
            })
        return data

    def get_valor_redondeado(self, obj):
        """Regla institucional: >= 0.5 redondea al entero superior."""
        return int(obj.valor.quantize(Decimal('1'), rounding=ROUND_HALF_UP))

    def get_estatus_rendimiento(self, obj):
        """
        Diferencia visual para el docente sobre el estado del alumno
        """
        nota = self.get_valor_redondeado(obj)
        if nota >= 8:
            return "APROBADO"
        elif 6 <= nota < 8:
            return "EN RIESGO"
        else:
            return "REPROBADO"


class ImportarCalificacionesSerializer(serializers.Serializer):
    """
    Maneja la carga masiva de notas desde archivos externos
    """
    actividad_id = serializers.UUIDField()
    archivo_excel = serializers.FileField()

    def validate_archivo_excel(self, value):
        """Valida extensiones permitidas para procesamiento automático."""
        extensiones_validas = ['.xlsx', '.xls', '.csv']
        if not any(value.name.lower().endswith(ext) for ext in extensiones_validas):
            raise serializers.ValidationError("Formato no soportado. Use Excel (.xlsx, .xls) o CSV.")
        return value
    
class ConcentradoAlumnoSerializer(serializers.Serializer):
    alumno_id = serializers.CharField()
    nombre_alumno = serializers.CharField()
    matricula = serializers.CharField()
    promedio_real = serializers.DecimalField(max_digits=5, decimal_places=2)
    promedio_redondeado = serializers.IntegerField()
    estatus = serializers.CharField()
    entregas = serializers.DictField()