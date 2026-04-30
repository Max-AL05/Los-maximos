"""
Generadores de archivos.

Cada función retorna un tuple (bytes, filename, mime_type) para que pueda
servirse igual desde REST (HttpResponse) o gRPC (FileResponse).
"""
from io import BytesIO


def generar_calificaciones_xlsx(materia_id) -> tuple[bytes, str, str]:
    # TODO:
    # 1. gRPC a MS-2 GetMateriaById → datos de la materia
    # 2. gRPC a MS-4 GetConcentrado(materia_id) → lista de alumnos con promedios
    # 3. Construir openpyxl.Workbook con encabezados institucionales
    buffer = BytesIO()
    # ...
    return (
        buffer.getvalue(),
        f"calificaciones_{materia_id}.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def generar_calificaciones_pdf(materia_id) -> tuple[bytes, str, str]:
    # TODO: usar reportlab.platypus para layout institucional
    buffer = BytesIO()
    return (buffer.getvalue(), f"calificaciones_{materia_id}.pdf", "application/pdf")


def generar_asistencias_xlsx(materia_id) -> tuple[bytes, str, str]:
    # TODO: gRPC a MS-5 GetEstadisticasAsistencia + listar Asistencias
    buffer = BytesIO()
    return (
        buffer.getvalue(),
        f"asistencias_{materia_id}.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def generar_asistencias_pdf(materia_id) -> tuple[bytes, str, str]:
    buffer = BytesIO()
    return (buffer.getvalue(), f"asistencias_{materia_id}.pdf", "application/pdf")


REGISTRO = {
    ("CALIFICACIONES", "XLSX"): generar_calificaciones_xlsx,
    ("CALIFICACIONES", "XLS"): generar_calificaciones_xlsx,
    ("CALIFICACIONES", "PDF"): generar_calificaciones_pdf,
    ("ASISTENCIAS", "XLSX"): generar_asistencias_xlsx,
    ("ASISTENCIAS", "XLS"): generar_asistencias_xlsx,
    ("ASISTENCIAS", "PDF"): generar_asistencias_pdf,
}
