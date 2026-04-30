"""
Servicers gRPC de MS-3 Docentes & Alumnos.

Implementan los métodos del contrato alumnos.proto:
    - GetAlumnosByMateria
    - GetAlumnoById
    - IsAlumnoEnMateria
"""
# from protos import alumnos_pb2, alumnos_pb2_grpc
# from apps.alumnos.models import Alumno, InscripcionMateria


# class AlumnosServicer(alumnos_pb2_grpc.AlumnosServiceServicer):
#     def GetAlumnosByMateria(self, request, context):
#         # TODO: InscripcionMateria.objects.filter(materia_id=...) -> AlumnosList
#         return alumnos_pb2.AlumnosList()
#
#     def GetAlumnoById(self, request, context):
#         # TODO: Alumno.objects.get(id=request.alumno_id)
#         return alumnos_pb2.AlumnoInfo()
#
#     def IsAlumnoEnMateria(self, request, context):
#         # TODO: InscripcionMateria.objects.filter(...).exists()
#         return alumnos_pb2.IsAlumnoEnMateriaResponse()
