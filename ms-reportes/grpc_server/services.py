"""
Servicers gRPC de MS-7 Reportes & Estadísticas.
"""
import grpc
from protos import reportes_pb2, reportes_pb2_grpc
from apps.reportes import services as reportes_services


class ReportesServicer(reportes_pb2_grpc.ReportesServiceServicer):

    def GenerateReport(self, request, context):
        fn = reportes_services.REGISTRO.get((request.tipo, request.formato))
        if not fn:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"Tipo/formato no soportado: {request.tipo}/{request.formato}")
            return reportes_pb2.FileResponse()

        try:
            file_bytes, filename, mime = fn(request.materia_id)
            return reportes_pb2.FileResponse(
                file_bytes=file_bytes,
                file_name=filename,
                mime_type=mime,
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return reportes_pb2.FileResponse()

    def GetHistorialDocente(self, request, context):
        # TODO: implementar cuando se defina el contrato completo
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        return reportes_pb2.HistorialResponse()