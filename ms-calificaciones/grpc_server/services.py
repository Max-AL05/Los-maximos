"""
Servicers gRPC de MS-4 Calificaciones.

Implementan los métodos del contrato calificaciones.proto:
    - GetConcentrado
    - GetPromedioAlumno
    - GetEstadisticasMateria
"""
# from protos import calificaciones_pb2, calificaciones_pb2_grpc


# class CalificacionesServicer(calificaciones_pb2_grpc.CalificacionesServiceServicer):
#     def GetConcentrado(self, request, context):
#         # TODO: misma lógica que el endpoint REST /concentrado pero retornando proto
#         return calificaciones_pb2.ConcentradoResponse()
#
#     def GetPromedioAlumno(self, request, context):
#         return calificaciones_pb2.PromedioResponse()
#
#     def GetEstadisticasMateria(self, request, context):
#         return calificaciones_pb2.EstadisticasMateria()
