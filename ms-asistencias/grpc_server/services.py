"""
Servicers gRPC de MS-5 Asistencias QR.

Implementan los métodos del contrato asistencias.proto:
    - GetAsistenciaAlumno
    - GetEstadisticasAsistencia
"""
# from protos import asistencias_pb2, asistencias_pb2_grpc
# from apps.asistencias.models import Asistencia


# class AsistenciasServicer(asistencias_pb2_grpc.AsistenciasServiceServicer):
#     def GetAsistenciaAlumno(self, request, context):
#         # TODO: Asistencia.objects.filter(alumno_id=..., materia_id=...)
#         return asistencias_pb2.AsistenciasList()
#
#     def GetEstadisticasAsistencia(self, request, context):
#         # TODO: aggregations sobre Asistencia + count de Sesion
#         return asistencias_pb2.EstadisticasAsistencia()
