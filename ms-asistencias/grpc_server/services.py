"""
Servicers gRPC de MS-5 Asistencias QR.

Implementan los métodos del contrato asistencias.proto:
    - GetAsistenciaAlumno      → historial de un alumno en una materia
    - GetEstadisticasAsistencia → estadísticas agregadas por materia

Consumido por: MS-7 Reportes (y cualquier MS que necesite estadísticas de asistencia).
"""
import grpc

from django.db.models import Count, Q

from protos import asistencias_pb2, asistencias_pb2_grpc
from apps.asistencias.models import Asistencia, EstadoAsistencia
from apps.sesiones.models import Sesion


class AsistenciasServicer(asistencias_pb2_grpc.AsistenciasServiceServicer):
    """
    Implementa el servicio gRPC AsistenciasService definido en asistencias.proto.
    """

    def GetAsistenciaAlumno(self, request, context):
        """
        Retorna la lista de asistencias de un alumno en una materia específica.

        Request fields:
            alumno_id  (str) → ID del alumno en MS-3
            materia_id (str) → ID de la materia en MS-2

        Response: AsistenciasList con lista de objetos Asistencia
            asistencia_id → UUID
            fecha         → ISO-8601 (YYYY-MM-DDTHH:MM:SS+00:00)
            estado        → PRESENTE | RETARDO | AUSENTE
            sesion_id     → UUID de la sesión asociada
        """
        alumno_id = request.alumno_id
        materia_id = request.materia_id

        # Validación básica de parámetros
        if not alumno_id or not materia_id:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("alumno_id y materia_id son requeridos.")
            return asistencias_pb2.AsistenciasList()

        # Consultar asistencias del alumno en la materia, ordenadas por fecha desc
        try:
            registros = Asistencia.objects.filter(
                alumno_id=alumno_id,
                materia_id=materia_id,
            ).select_related("sesion").order_by("-fecha")

            # Mapear cada registro ORM al mensaje protobuf Asistencia
            asistencias_pb = []
            for registro in registros:
                asistencias_pb.append(
                    asistencias_pb2.Asistencia(
                        asistencia_id=str(registro.id),
                        fecha=registro.fecha.isoformat(),
                        estado=registro.estado,                # ya es str: PRESENTE|RETARDO|AUSENTE
                        sesion_id=str(registro.sesion_id),
                    )
                )

            return asistencias_pb2.AsistenciasList(asistencias=asistencias_pb)

        except Exception as exc:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error interno al consultar asistencias: {exc}")
            return asistencias_pb2.AsistenciasList()

    def GetEstadisticasAsistencia(self, request, context):
        """
        Calcula y retorna estadísticas agregadas de asistencia para una materia.

        Request fields:
            materia_id (str) → ID de la materia

        Response: EstadisticasAsistencia
            materia_id           → ID de la materia
            total_sesiones       → Número de sesiones realizadas (cerradas o activas)
            total_asistencias    → Registros con estado PRESENTE
            total_retardos       → Registros con estado RETARDO
            total_ausencias      → Registros con estado AUSENTE
            porcentaje_asistencia → (presentes + retardos) / (presentes + retardos + ausentes) * 100
        """
        materia_id = request.materia_id

        if not materia_id:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("materia_id es requerido.")
            return asistencias_pb2.EstadisticasAsistencia()

        try:
            # Contar total de sesiones para esta materia
            total_sesiones = Sesion.objects.filter(materia_id=materia_id).count()

            # Contar asistencias por estado usando aggregación Django ORM
            conteos = Asistencia.objects.filter(materia_id=materia_id).aggregate(
                presentes=Count("id", filter=Q(estado=EstadoAsistencia.PRESENTE)),
                retardos=Count("id", filter=Q(estado=EstadoAsistencia.RETARDO)),
                ausencias=Count("id", filter=Q(estado=EstadoAsistencia.AUSENTE)),
            )

            total_presentes = conteos["presentes"] or 0
            total_retardos = conteos["retardos"] or 0
            total_ausencias = conteos["ausencias"] or 0

            # Total de registros que cuentan como "asistió" (presente o retardo)
            total_asistio = total_presentes + total_retardos
            total_registros = total_asistio + total_ausencias

            # Calcular porcentaje (0 si no hay registros para evitar división por cero)
            if total_registros > 0:
                porcentaje = (total_asistio / total_registros) * 100.0
            else:
                porcentaje = 0.0

            return asistencias_pb2.EstadisticasAsistencia(
                materia_id=materia_id,
                total_sesiones=total_sesiones,
                total_asistencias=total_presentes,
                total_retardos=total_retardos,
                total_ausencias=total_ausencias,
                porcentaje_asistencia=round(porcentaje, 2),
            )

        except Exception as exc:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error al calcular estadísticas: {exc}")
            return asistencias_pb2.EstadisticasAsistencia()