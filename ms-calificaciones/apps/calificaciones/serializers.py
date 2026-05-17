"""
Serializadores DRF.

OJO: la lógica de estatus y redondeo vive en `apps.calificaciones.services`
para que REST, serializers, modelos y el servicer gRPC compartan la misma
implementación. Cualquier cambio de umbrales se hace ahí, no aquí.
"""
from decimal import Decimal, ROUND_HALF_UP

from rest_framework import serializers

from .models import Actividad, Calificacion
from .services import calcular_estatus, redondeo_institucional


class ActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actividad
        fields = "__all__"
        read_only_fields = ("id", "created_at")

    def validate_valor_maximo(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "El valor máximo de la actividad debe ser mayor a 0."
            )
        return value


class CalificacionSerializer(serializers.ModelSerializer):
    valor_redondeado    = serializers.SerializerMethodField()
    estatus_rendimiento = serializers.SerializerMethodField()

    class Meta:
        model = Calificacion
        fields = (
            "id", "actividad", "alumno_id", "valor",
            "valor_redondeado", "estatus_rendimiento",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, data):
        actividad = data.get("actividad")
        valor = data.get("valor")

        # En PATCH parcial puede no venir actividad/valor; sólo valida si vienen.
        if actividad and valor is not None and valor > actividad.valor_maximo:
            raise serializers.ValidationError({
                "valor": (
                    f"La calificación ({valor}) no puede ser mayor al valor "
                    f"máximo de la actividad ({actividad.valor_maximo})."
                )
            })
        if valor is not None and valor < 0:
            raise serializers.ValidationError({"valor": "La calificación no puede ser negativa."})
        return data

    def get_valor_redondeado(self, obj) -> int:
        return redondeo_institucional(obj.valor)

    def get_estatus_rendimiento(self, obj) -> str:
        return calcular_estatus(self.get_valor_redondeado(obj))


class ImportarCalificacionesSerializer(serializers.Serializer):
    actividad_id  = serializers.UUIDField()
    archivo_excel = serializers.FileField()

    def validate_archivo_excel(self, value):
        permitidas = (".xlsx", ".xls", ".csv")
        if not value.name.lower().endswith(permitidas):
            raise serializers.ValidationError(
                "Formato no soportado. Usa Excel (.xlsx, .xls) o CSV."
            )
        return value


class ConcentradoAlumnoSerializer(serializers.Serializer):
    """
    Salida del endpoint GET /concentrado/<materia_id>/.

    Los campos vienen ya calculados por `CalificacionesService`.
    Si en el futuro se quiere recalcular el estatus aquí, hacerlo con
    `calcular_estatus(...)` para no duplicar la regla.
    """
    alumno_id           = serializers.CharField()
    matricula           = serializers.CharField()
    nombre_completo     = serializers.CharField()
    nombre_alumno       = serializers.CharField()         # alias compatibilidad
    promedio_real       = serializers.DecimalField(max_digits=5, decimal_places=2)
    promedio_redondeado = serializers.IntegerField()
    estatus             = serializers.CharField()         # APROBADO | EN_RIESGO | REPROBADO
    entregas            = serializers.DictField(
        child=serializers.DecimalField(max_digits=5, decimal_places=2),
        required=False,
    )