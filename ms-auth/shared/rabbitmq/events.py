"""
AGM – Contratos de eventos RabbitMQ.

Este archivo documenta y centraliza las routing keys y la estructura
de payload de cada evento publicado en el exchange 'agm.events'.

Exchange: agm.events  (type: topic, durable: true)

─────────────────────────────────────────────────────────────────────
EVENTO: alumno.registrado
Productor:  MS-3 Docentes & Alumnos
Consumidor: MS-6 Notificaciones → envía correo de bienvenida
─────────────────────────────────────────────────────────────────────
Payload:
{
    "alumno_id":      "uuid",
    "alumno_email":   "alumno@alumno.buap.mx",
    "alumno_nombre":  "Juan Pérez",
    "materia_id":     "uuid",
    "materia_nombre": "Servicios Web",
    "clave_unica":    "aB3kXz9qLm"
}

─────────────────────────────────────────────────────────────────────
EVENTO: alumno.baja
Productor:  MS-3 Docentes & Alumnos
Consumidor: MS-6 Notificaciones → avisa al docente
─────────────────────────────────────────────────────────────────────
Payload:
{
    "alumno_id":      "uuid",
    "alumno_nombre":  "Juan Pérez",
    "materia_id":     "uuid",
    "materia_nombre": "Servicios Web",
    "docente_id":     "uuid",
    "docente_email":  "docente@cs.buap.mx",
    "docente_nombre": "Dr. García",
    "motivo":         "solicitud voluntaria"
}

─────────────────────────────────────────────────────────────────────
EVENTO: materia.cerrada
Productor:  MS-2 Periodos & Materias
Consumidor: MS-6 Notificaciones → notifica a todos los alumnos
─────────────────────────────────────────────────────────────────────
Payload:
{
    "materia_id":     "uuid",
    "materia_nombre": "Servicios Web",
    "periodo":        "2025-I",
    "alumnos": [
        {
            "email":              "alumno@alumno.buap.mx",
            "nombre":             "Juan Pérez",
            "calificacion_final": 9
        }
    ]
}

─────────────────────────────────────────────────────────────────────
EVENTO: auth.reset_password
Productor:  MS-1 Auth & Users
Consumidor: MS-6 Notificaciones → envía link de recuperación
─────────────────────────────────────────────────────────────────────
Payload:
{
    "user_id":     "uuid",
    "user_email":  "usuario@buap.mx",
    "user_nombre": "Dr. García",
    "reset_link":  "https://agm.buap.mx/reset?token=abc123"
}

─────────────────────────────────────────────────────────────────────
EVENTO: reporte.generado
Productor:  MS-7 Reportes & Estadísticas
Consumidor: MS-6 Notificaciones → avisa al docente que su reporte está listo
─────────────────────────────────────────────────────────────────────
Payload:
{
    "reporte_id":     "uuid",
    "tipo":           "CALIFICACIONES",
    "formato":        "PDF",
    "materia_id":     "uuid",
    "materia_nombre": "Servicios Web",
    "docente_id":     "uuid",
    "docente_email":  "docente@cs.buap.mx",
    "docente_nombre": "Dr. García",
    "file_name":      "calificaciones_sw_2025I.pdf",
    "generado_en":    "2025-06-01T10:30:00Z"
}
"""

# Constantes de routing keys para importar desde los productores
ALUMNO_REGISTRADO  = "alumno.registrado"
ALUMNO_BAJA        = "alumno.baja"
MATERIA_CERRADA    = "materia.cerrada"
AUTH_RESET_PASSWORD = "auth.reset_password"
REPORTE_GENERADO   = "reporte.generado"
