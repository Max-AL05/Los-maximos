"""
Servicers gRPC de MS-4 Calificaciones & Ponderaciones.

    - GetConcentrado        → lista de alumnos con promedio ponderado
    - GetPromedioAlumno     → promedio de un alumno en una materia
    - GetEstadisticasMateria → estadísticas del grupo
"""
import grpc
from decimal import Decimal

from apps.calificaciones.models import Actividad, Calificacion
from apps.calificaciones.views import _calcular_concentrado, _redondear_institucional
from apps.ponderaciones.models import Ponderacion
from protos import calificaciones_pb2, calificaciones_pb2_grpc


class CalificacionesServicer(calificaciones_pb2_grpc.CalificacionesServiceServicer):

    def GetConcentrado(self, request, context):
        try:
            alumnos = _calcular_concentrado(request.materia_id)
            return calificaciones_pb2.ConcentradoResponse(
                alumnos=[
                    calificaciones_pb2.AlumnoCalif(
                        alumno_id=a["alumno_id"],
                        matricula=a["matricula"],
                        nombre_completo=a["nombre_completo"],
                        promedio_real=a["promedio_real"],
                        promedio_redondeado=a["promedio_redondeado"],
                        estado=a["estado"],
                    )
                    for a in alumnos
                ]
            )
        except Exception:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Error al calcular el concentrado")
            return calificaciones_pb2.ConcentradoResponse()

    def GetPromedioAlumno(self, request, context):
        try:
            concentrado = _calcular_concentrado(request.materia_id)
            alumno = next((a for a in concentrado if a["alumno_id"] == request.alumno_id), None)
            if not alumno:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Alumno no encontrado en la materia")
                return calificaciones_pb2.PromedioResponse()
            return calificaciones_pb2.PromedioResponse(
                promedio_real=alumno["promedio_real"],
                promedio_redondeado=alumno["promedio_redondeado"],
            )
        except Exception:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Error al obtener el promedio")
            return calificaciones_pb2.PromedioResponse()

    def GetEstadisticasMateria(self, request, context):
        try:
            concentrado = _calcular_concentrado(request.materia_id)
            if not concentrado:
                return calificaciones_pb2.EstadisticasMateria(
                    materia_id=request.materia_id,
                    total_alumnos=0,
                )
            promedios = [a["promedio_real"] for a in concentrado]
            aprobados  = sum(1 for a in concentrado if a["promedio_redondeado"] >= 6)
            reprobados = len(concentrado) - aprobados
            return calificaciones_pb2.EstadisticasMateria(
                materia_id=request.materia_id,
                total_alumnos=len(concentrado),
                aprobados=aprobados,
                reprobados=reprobados,
                promedio_grupal=sum(promedios) / len(promedios),
                calificacion_maxima=max(promedios),
                calificacion_minima=min(promedios),
            )
        except Exception:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Error al calcular estadísticas")
            return calificaciones_pb2.EstadisticasMateria()
