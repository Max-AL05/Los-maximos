"""
Servicers gRPC de MS-7 Reportes & Estadísticas.

Implementan los métodos del contrato reportes.proto:
    - GenerateReport
    - GetHistorialDocente
"""
# from protos import reportes_pb2, reportes_pb2_grpc
# from apps.reportes import services as reportes_services
# from apps.estadisticas.models import EstadisticaPeriodo


# class ReportesServicer(reportes_pb2_grpc.ReportesServiceServicer):
#     def GenerateReport(self, request, context):
#         fn = reportes_services.REGISTRO.get((request.tipo, request.formato))
#         if not fn:
#             context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
#             return reportes_pb2.FileResponse()
#         file_bytes, filename, mime = fn(request.materia_id)
#         return reportes_pb2.FileResponse(
#             file_bytes=file_bytes, file_name=filename, mime_type=mime,
#         )
#
#     def GetHistorialDocente(self, request, context):
#         qs = EstadisticaPeriodo.objects.filter(docente_id=request.docente_id)
#         # TODO: serializar a StatsPeriodo
#         return reportes_pb2.HistorialResponse()
