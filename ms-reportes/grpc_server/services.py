"""
Servicers gRPC de MS-7 Reportes & Estadísticas.
Expone dos métodos hacia otros microservicios:
    - GenerateReport      → genera y retorna bytes de un archivo Excel o PDF
    - GetHistorialDocente → retorna el historial estadístico de un docente
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import grpc
from protos import reportes_pb2, reportes_pb2_grpc
from apps.reportes import services as reportes_services
from apps.estadisticas.models import EstadisticaPeriodo


class ReportesServicer(reportes_pb2_grpc.ReportesServiceServicer):

    def GenerateReport(self, request, context):
        """
        Genera un archivo Excel o PDF y retorna sus bytes.
        request.tipo    → CALIFICACIONES | ASISTENCIAS
        request.formato → PDF | XLS | XLSX
        request.materia_id
        """
        fn = reportes_services.REGISTRO.get((request.tipo, request.formato))
        if not fn:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(
                f"Tipo/formato no soportado: {request.tipo}/{request.formato}"
            )
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
        """
        Retorna el historial estadístico de un docente por periodo.
        Lee del caché local EstadisticaPeriodo.
        request.docente_id
        """
        try:
            qs = EstadisticaPeriodo.objects.filter(
                docente_id=request.docente_id
            ).order_by("periodo_id", "materia_id")

            historial = [
                reportes_pb2.StatsPeriodo(
                    periodo_id=str(ep.periodo_id),
                    periodo_nombre=str(ep.periodo_id),
                    materia_id=str(ep.materia_id),
                    materia_nombre="",
                    total_alumnos=ep.total_alumnos,
                    promedio_grupal=float(ep.promedio_grupal),
                    porcentaje_asistencia=float(ep.porcentaje_asistencia),
                )
                for ep in qs
            ]
            return reportes_pb2.HistorialResponse(historial=historial)

        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return reportes_pb2.HistorialResponse()