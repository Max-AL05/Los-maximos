"""
Servicers gRPC de MS-3 Docentes & Alumnos.

Implementan los métodos del contrato alumnos.proto:
    - GetAlumnosByMateria  → lista de alumnos activos inscritos en una materia
    - GetAlumnoById        → datos de un alumno por UUID
    - IsAlumnoEnMateria    → verifica si un alumno está inscrito (y si no fue baja)
"""
import grpc

from apps.alumnos.models import Alumno, InscripcionMateria
from protos import alumnos_pb2, alumnos_pb2_grpc


def _alumno_to_proto(a: Alumno, activo_en_materia: bool = True) -> alumnos_pb2.AlumnoInfo:
    return alumnos_pb2.AlumnoInfo(
        alumno_id         = str(a.id),
        matricula         = a.matricula,
        nombre_completo   = a.nombre_completo,
        correo            = a.correo,
        tipo_formacion    = a.tipo_formacion or "",
        activo_en_materia = activo_en_materia,
    )


class AlumnosServicer(alumnos_pb2_grpc.AlumnosServiceServicer):

    def GetAlumnosByMateria(self, request, context):
        try:
            inscripciones = (
                InscripcionMateria.objects
                .filter(materia_id=request.materia_id, dado_de_baja=False)
                .select_related("alumno")
            )
            return alumnos_pb2.AlumnosList(
                alumnos=[_alumno_to_proto(i.alumno, activo_en_materia=True) for i in inscripciones]
            )
        except Exception:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Error interno al listar alumnos de la materia")
            return alumnos_pb2.AlumnosList()

    def GetAlumnoById(self, request, context):
        try:
            alumno = Alumno.objects.get(id=request.alumno_id)
            return _alumno_to_proto(alumno)
        except Alumno.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Alumno {request.alumno_id} no encontrado")
            return alumnos_pb2.AlumnoInfo()
        except Exception:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Error interno al buscar el alumno")
            return alumnos_pb2.AlumnoInfo()

    def IsAlumnoEnMateria(self, request, context):
        try:
            inscripcion = InscripcionMateria.objects.filter(
                alumno_id=request.alumno_id,
                materia_id=request.materia_id,
            ).first()
            if not inscripcion:
                return alumnos_pb2.IsAlumnoEnMateriaResponse(
                    inscrito=False, dado_de_baja=False,
                )
            return alumnos_pb2.IsAlumnoEnMateriaResponse(
                inscrito=not inscripcion.dado_de_baja,
                dado_de_baja=inscripcion.dado_de_baja,
            )
        except Exception:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Error interno al verificar inscripción")
            return alumnos_pb2.IsAlumnoEnMateriaResponse()