from rest_framework import viewsets
from rest_framework.permissions import AllowAny 
from .models import Materia
from .serializers import MateriaSerializer


class MateriaViewSet(viewsets.ModelViewSet):
    queryset = Materia.objects.select_related("periodo").all()
    serializer_class = MateriaSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params

        periodo_id = params.get("periodo")
        if periodo_id:
            qs = qs.filter(periodo_id=periodo_id)

        docente_id = params.get("docente_id")
        if docente_id:
            qs = qs.filter(docente_id=docente_id)

        estado = params.get("estado")
        if estado:
            qs = qs.filter(estado=estado)

        return qs
    def update(self, request, *args, **kwargs):
        """
        Override de update: cuando el estado cambia a CERRADA,
        publica evento 'materia.cerrada' en RabbitMQ para que
        MS-6 notifique asincronamente a todos los alumnos.
        """
        materia = self.get_object()
        estado_previo = materia.estado
        response = super().update(request, *args, **kwargs)

        nuevo_estado = request.data.get("estado") or (
            response.data.get("estado") if response.status_code < 300 else None
        )

        if estado_previo != "CERRADA" and nuevo_estado == "CERRADA":
            try:
                from shared.rabbitmq.publisher import publish_event
                from shared.rabbitmq.events import MATERIA_CERRADA
                # Obtener lista de alumnos via gRPC desde MS-3 para el payload
                # (intentamos; si falla, MS-6 puede consultarlos directamente)
                publish_event(MATERIA_CERRADA, {
                    "materia_id":     str(materia.id),
                    "materia_nombre": materia.nombre,
                    "periodo":        str(materia.periodo) if materia.periodo else "",
                    "alumnos": [],  # MS-6 consulta via gRPC GetAlumnosByMateria si viene vacio
                })
            except Exception:
                pass  # El cierre persiste aunque RabbitMQ no este disponible

        return response
