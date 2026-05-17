"""
Clientes gRPC del MS-7 Reportes.

Consume datos de:
  MS-2 Periodos       → get_materia()
  MS-3 Alumnos        → get_alumnos_by_materia(), get_materias_alumno()
  MS-4 Calificaciones → get_concentrado(), get_estadisticas_materia(), get_promedio_alumno()
  MS-5 Asistencias    → get_asistencia_alumno(), get_estadisticas_asistencia()

Cuando USE_FALLBACK = True todas las funciones devuelven datos demo
con la estructura exacta que services.py necesita, sin necesidad de
que los demás MS estén corriendo.
"""
from __future__ import annotations

import logging
import os
import sys

import grpc
from django.conf import settings

_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _BASE)
sys.path.insert(0, os.path.join(_BASE, "protos"))

try:
    from protos import periodos_pb2, periodos_pb2_grpc
    from protos import alumnos_pb2, alumnos_pb2_grpc
    from protos import calificaciones_pb2, calificaciones_pb2_grpc
    from protos import asistencias_pb2, asistencias_pb2_grpc
    PROTOS_OK = True
except ImportError as exc:
    logging.warning("[grpc_clients] No se pudieron importar los protos: %s", exc)
    PROTOS_OK = False

# Cambiar a False cuando todos los MS estén corriendo
USE_FALLBACK = True

# ─── Demo data ────────────────────────────────────────────────────────────────
_DEMO_MATERIA = {
    "id":         "demo-001",
    "nrc":        "48308",
    "clave":      "CC501",
    "nombre":     "Desarrollo de Sitios Web",
    "seccion":    "001",
    "periodo_id": "PRI-2026",
    "horario":    "Lun-Mie 10:00-12:00",
    "estado":     "ACTIVA",
}

_DEMO_ALUMNOS = [
    {"alumno_id": "001", "nombre_completo": "AGUILAR SALDIVAR ANGEL G.",       "matricula": "202224429"},
    {"alumno_id": "002", "nombre_completo": "AMADOR LAGUNES ALEJANDRO",        "matricula": "202213377"},
    {"alumno_id": "003", "nombre_completo": "AVENDAÑO VEGA ERWIN G.",          "matricula": "202220926"},
    {"alumno_id": "004", "nombre_completo": "CONTRERAS GONZALEZ GERSON E.",    "matricula": "202237583"},
    {"alumno_id": "005", "nombre_completo": "ESCUDERO RIVERA ALFREDO",         "matricula": "202222184"},
    {"alumno_id": "006", "nombre_completo": "FLORES MENDOZA BRENDA L.",        "matricula": "202231045"},
]

_DEMO_CONCENTRADO = [
    {"matricula": "202224429", "nombre_completo": "AGUILAR SALDIVAR ANGEL G.",    "promedio_real": 9.3, "promedio_redondeado": 9,  "estado": "APROBADO"},
    {"matricula": "202213377", "nombre_completo": "AMADOR LAGUNES ALEJANDRO",     "promedio_real": 7.8, "promedio_redondeado": 8,  "estado": "APROBADO"},
    {"matricula": "202220926", "nombre_completo": "AVENDAÑO VEGA ERWIN G.",       "promedio_real": 5.4, "promedio_redondeado": 5,  "estado": "REPROBADO"},
    {"matricula": "202237583", "nombre_completo": "CONTRERAS GONZALEZ GERSON E.", "promedio_real": 8.5, "promedio_redondeado": 9,  "estado": "APROBADO"},
    {"matricula": "202222184", "nombre_completo": "ESCUDERO RIVERA ALFREDO",      "promedio_real": 6.0, "promedio_redondeado": 6,  "estado": "APROBADO"},
    {"matricula": "202231045", "nombre_completo": "FLORES MENDOZA BRENDA L.",     "promedio_real": 9.7, "promedio_redondeado": 10, "estado": "APROBADO"},
]

_DEMO_STATS_MATERIA = {
    "total_alumnos":       6,
    "aprobados":           5,
    "reprobados":          1,
    "promedio_grupal":     7.78,
    "calificacion_maxima": 9.7,
    "calificacion_minima": 5.4,
}

_DEMO_ASISTENCIAS_POR_ALUMNO = {
    "001": [{"estado": "PRESENTE"}, {"estado": "PRESENTE"}, {"estado": "RETARDO"},  {"estado": "PRESENTE"}, {"estado": "PRESENTE"}],
    "002": [{"estado": "PRESENTE"}, {"estado": "AUSENTE"},  {"estado": "PRESENTE"}, {"estado": "PRESENTE"}, {"estado": "RETARDO"}],
    "003": [{"estado": "AUSENTE"},  {"estado": "AUSENTE"},  {"estado": "PRESENTE"}, {"estado": "AUSENTE"},  {"estado": "PRESENTE"}],
    "004": [{"estado": "PRESENTE"}, {"estado": "PRESENTE"}, {"estado": "PRESENTE"}, {"estado": "PRESENTE"}, {"estado": "PRESENTE"}],
    "005": [{"estado": "RETARDO"},  {"estado": "PRESENTE"}, {"estado": "PRESENTE"}, {"estado": "AUSENTE"},  {"estado": "PRESENTE"}],
    "006": [{"estado": "PRESENTE"}, {"estado": "PRESENTE"}, {"estado": "PRESENTE"}, {"estado": "PRESENTE"}, {"estado": "RETARDO"}],
}

_DEMO_STATS_ASISTENCIA = {
    "total_sesiones":        5,
    "total_asistencias":     22,
    "total_retardos":        4,
    "total_ausencias":       4,
    "porcentaje_asistencia": 86.7,
}


# ─── Helper de canal ──────────────────────────────────────────────────────────
def _channel(service_key: str):
    """Abre un canal gRPC usando el target definido en settings.GRPC_TARGETS."""
    target = settings.GRPC_TARGETS.get(service_key, "localhost:50051")
    return grpc.insecure_channel(target)


# ─── MS-2 Periodos ────────────────────────────────────────────────────────────
def get_materia(materia_id: str) -> dict:
    """Datos de una materia desde MS-2."""
    if USE_FALLBACK or not PROTOS_OK:
        return _DEMO_MATERIA
    try:
        with _channel("periodos") as ch:
            stub = periodos_pb2_grpc.PeriodosServiceStub(ch)
            r = stub.GetMateriaById(periodos_pb2.MateriaRequest(id=materia_id))
            return {
                "id": r.id, "nrc": r.nrc, "clave": r.clave,
                "nombre": r.nombre, "seccion": r.seccion,
                "periodo_id": r.periodo_id, "horario": r.horario, "estado": r.estado,
            }
    except Exception as e:
        logging.warning("[grpc_clients] get_materia falló: %s", e)
        return _DEMO_MATERIA


# ─── MS-3 Alumnos ─────────────────────────────────────────────────────────────
def get_alumnos_by_materia(materia_id: str) -> list[dict]:
    """Lista de alumnos de una materia desde MS-3.
    Retorna: [{alumno_id, nombre_completo, matricula}]
    """
    if USE_FALLBACK or not PROTOS_OK:
        return _DEMO_ALUMNOS
    try:
        with _channel("alumnos") as ch:
            stub = alumnos_pb2_grpc.AlumnosServiceStub(ch)
            resp = stub.GetAlumnosByMateria(alumnos_pb2.MateriaRequest(materia_id=materia_id))
            return [
                {"alumno_id": a.id, "nombre_completo": a.nombre, "matricula": a.matricula}
                for a in resp.alumnos
            ]
    except Exception as e:
        logging.warning("[grpc_clients] get_alumnos_by_materia falló: %s", e)
        return _DEMO_ALUMNOS


def get_materias_alumno(alumno_id: str) -> list[dict]:
    """Materias inscritas de un alumno (para estadísticas individuales)."""
    if USE_FALLBACK or not PROTOS_OK:
        return [_DEMO_MATERIA]
    try:
        with _channel("alumnos") as ch:
            stub = alumnos_pb2_grpc.AlumnosServiceStub(ch)
            resp = stub.GetMateriasByAlumno(alumnos_pb2.AlumnoRequest(alumno_id=alumno_id))
            return [{"id": m.id, "nombre": m.nombre} for m in resp.materias]
    except Exception as e:
        logging.warning("[grpc_clients] get_materias_alumno falló: %s", e)
        return [_DEMO_MATERIA]


# ─── MS-4 Calificaciones ──────────────────────────────────────────────────────
def get_concentrado(materia_id: str) -> list[dict]:
    """Concentrado de calificaciones finales desde MS-4.
    Retorna: [{matricula, nombre_completo, promedio_real, promedio_redondeado, estado}]
    """
    if USE_FALLBACK or not PROTOS_OK:
        return _DEMO_CONCENTRADO
    try:
        with _channel("calificaciones") as ch:
            stub = calificaciones_pb2_grpc.CalificacionesServiceStub(ch)
            resp = stub.GetConcentrado(calificaciones_pb2.ConcentradoRequest(materia_id=materia_id))
            return [
                {
                    "matricula":           c.matricula,
                    "nombre_completo":     c.nombre_completo,
                    "promedio_real":       c.promedio_real,
                    "promedio_redondeado": c.promedio_redondeado,
                    "estado":              c.estado,
                }
                for c in resp.calificaciones
            ]
    except Exception as e:
        logging.warning("[grpc_clients] get_concentrado falló: %s", e)
        return _DEMO_CONCENTRADO


def get_estadisticas_materia(materia_id: str) -> dict:
    """Estadísticas grupales de calificaciones desde MS-4.
    Retorna: {total_alumnos, aprobados, reprobados, promedio_grupal,
              calificacion_maxima, calificacion_minima}
    """
    if USE_FALLBACK or not PROTOS_OK:
        return _DEMO_STATS_MATERIA
    try:
        with _channel("calificaciones") as ch:
            stub = calificaciones_pb2_grpc.CalificacionesServiceStub(ch)
            r = stub.GetEstadisticasMateria(
                calificaciones_pb2.EstadisticasRequest(materia_id=materia_id)
            )
            return {
                "total_alumnos":       r.total_alumnos,
                "aprobados":           r.aprobados,
                "reprobados":          r.reprobados,
                "promedio_grupal":     r.promedio_grupal,
                "calificacion_maxima": r.calificacion_maxima,
                "calificacion_minima": r.calificacion_minima,
            }
    except Exception as e:
        logging.warning("[grpc_clients] get_estadisticas_materia falló: %s", e)
        return _DEMO_STATS_MATERIA


def get_promedio_alumno(materia_id: str, alumno_id: str) -> float:
    """Promedio ponderado de un alumno en una materia."""
    if USE_FALLBACK or not PROTOS_OK:
        return 8.5
    try:
        with _channel("calificaciones") as ch:
            stub = calificaciones_pb2_grpc.CalificacionesServiceStub(ch)
            r = stub.GetPromedioAlumno(
                calificaciones_pb2.PromedioRequest(materia_id=materia_id, alumno_id=alumno_id)
            )
            return r.promedio
    except Exception as e:
        logging.warning("[grpc_clients] get_promedio_alumno falló: %s", e)
        return 0.0


# ─── MS-5 Asistencias ─────────────────────────────────────────────────────────
def get_asistencia_alumno(alumno_id: str, materia_id: str) -> list[dict]:
    """Registros de asistencia de un alumno desde MS-5.
    Retorna: [{estado}]  donde estado ∈ {PRESENTE, RETARDO, AUSENTE}
    """
    if USE_FALLBACK or not PROTOS_OK:
        return _DEMO_ASISTENCIAS_POR_ALUMNO.get(alumno_id, [{"estado": "AUSENTE"}] * 5)
    try:
        with _channel("asistencias") as ch:
            stub = asistencias_pb2_grpc.AsistenciasServiceStub(ch)
            resp = stub.GetAsistenciaAlumno(
                asistencias_pb2.AsistenciaAlumnoRequest(alumno_id=alumno_id, materia_id=materia_id)
            )
            return [{"estado": r.estado} for r in resp.registros]
    except Exception as e:
        logging.warning("[grpc_clients] get_asistencia_alumno falló: %s", e)
        return []


def get_estadisticas_asistencia(materia_id: str) -> dict:
    """Resumen grupal de asistencias desde MS-5.
    Retorna: {total_sesiones, total_asistencias, total_retardos,
              total_ausencias, porcentaje_asistencia}
    """
    if USE_FALLBACK or not PROTOS_OK:
        return _DEMO_STATS_ASISTENCIA
    try:
        with _channel("asistencias") as ch:
            stub = asistencias_pb2_grpc.AsistenciasServiceStub(ch)
            r = stub.GetEstadisticasAsistencia(
                asistencias_pb2.EstadisticasRequest(materia_id=materia_id)
            )
            return {
                "total_sesiones":        r.total_sesiones,
                "total_asistencias":     r.total_asistencias,
                "total_retardos":        r.total_retardos,
                "total_ausencias":       r.total_ausencias,
                "porcentaje_asistencia": r.porcentaje_asistencia,
            }
    except Exception as e:
        logging.warning("[grpc_clients] get_estadisticas_asistencia falló: %s", e)
        return _DEMO_STATS_ASISTENCIA