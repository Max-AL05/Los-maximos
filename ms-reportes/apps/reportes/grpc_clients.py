from __future__ import annotations

import logging
import os
import sys
import grpc
from django.conf import settings

# Agregar la raíz del proyecto al path para que encuentre la carpeta protos/
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
    
    # ─── Configuración de fallback ───────────────────────────────────────────────
USE_FALLBACK = True  # cambiar a False cuando los demás MS estén corriendo

# ─── Datos demo ──────────────────────────────────────────────────────────────
_DEMO_MATERIA = {"id": "demo-001", "nombre": "Desarrollo de Sitios Web", "nrc": "48308", "seccion": "OO1", "periodo": "Primavera 2026"}
_DEMO_ALUMNOS = [
    {"id": "001", "nombre": "AGUILAR SALDIVAR ANGEL G.", "matricula": "202224429"},
    {"id": "002", "nombre": "AMADOR LAGUNES ALEJANDRO", "matricula": "202213377"},
    {"id": "003", "nombre": "AVENDAÑO VEGA ERWIN G.", "matricula": "202220926"},
    {"id": "004", "nombre": "CONTRERAS GONZALEZ GERSON E.", "matricula": "202237583"},
    {"id": "005", "nombre": "ESCUDERO RIVERA ALFREDO", "matricula": "202222184"},
]


def _channel(host_key: str, port_key: str):
    host = getattr(settings, host_key, "localhost")
    port = getattr(settings, port_key, 50051)
    return grpc.insecure_channel(f"{host}:{port}")


# ─── MS-2 Periodos ───────────────────────────────────────────────────────────
def get_materia_by_id(materia_id: str) -> dict:
    if USE_FALLBACK or not PROTOS_OK:
        return _DEMO_MATERIA
    try:
        with _channel("GRPC_PERIODOS_HOST", "GRPC_PERIODOS_PORT") as ch:
            stub = periodos_pb2_grpc.PeriodosServiceStub(ch)
            resp = stub.GetMateriaById(periodos_pb2.MateriaRequest(id=materia_id))
            return {"id": resp.id, "nombre": resp.nombre, "nrc": resp.nrc, "seccion": resp.seccion, "periodo": resp.periodo}
    except Exception as e:
        logging.warning("[grpc_clients] get_materia_by_id falló: %s", e)
        return _DEMO_MATERIA


# ─── MS-3 Alumnos ────────────────────────────────────────────────────────────
def get_alumnos_by_materia(materia_id: str) -> list:
    if USE_FALLBACK or not PROTOS_OK:
        return _DEMO_ALUMNOS
    try:
        with _channel("GRPC_ALUMNOS_HOST", "GRPC_ALUMNOS_PORT") as ch:
            stub = alumnos_pb2_grpc.AlumnosServiceStub(ch)
            resp = stub.GetAlumnosByMateria(alumnos_pb2.MateriaRequest(materia_id=materia_id))
            return [{"id": a.id, "nombre": a.nombre, "matricula": a.matricula} for a in resp.alumnos]
    except Exception as e:
        logging.warning("[grpc_clients] get_alumnos_by_materia falló: %s", e)
        return _DEMO_ALUMNOS


def get_materias_alumno(alumno_id: str) -> list:
    if USE_FALLBACK or not PROTOS_OK:
        return [_DEMO_MATERIA]
    try:
        with _channel("GRPC_ALUMNOS_HOST", "GRPC_ALUMNOS_PORT") as ch:
            stub = alumnos_pb2_grpc.AlumnosServiceStub(ch)
            resp = stub.GetMateriasByAlumno(alumnos_pb2.AlumnoRequest(alumno_id=alumno_id))
            return [{"id": m.id, "nombre": m.nombre} for m in resp.materias]
    except Exception as e:
        logging.warning("[grpc_clients] get_materias_alumno falló: %s", e)
        return [_DEMO_MATERIA]


# ─── MS-4 Calificaciones ─────────────────────────────────────────────────────
def get_concentrado_calificaciones(materia_id: str) -> list:
    if USE_FALLBACK or not PROTOS_OK:
        return [{"alumno_id": a["id"], "nombre": a["nombre"], "matricula": a["matricula"], "promedio": round(7.5 + i * 0.3, 1)} for i, a in enumerate(_DEMO_ALUMNOS)]
    try:
        with _channel("GRPC_CALIFICACIONES_HOST", "GRPC_CALIFICACIONES_PORT") as ch:
            stub = calificaciones_pb2_grpc.CalificacionesServiceStub(ch)
            resp = stub.GetConcentrado(calificaciones_pb2.ConcentradoRequest(materia_id=materia_id))
            return [{"alumno_id": c.alumno_id, "nombre": c.nombre, "matricula": c.matricula, "promedio": c.promedio} for c in resp.calificaciones]
    except Exception as e:
        logging.warning("[grpc_clients] get_concentrado_calificaciones falló: %s", e)
        return []


def get_promedio_alumno(materia_id: str, alumno_id: str) -> float:
    if USE_FALLBACK or not PROTOS_OK:
        return 8.5
    try:
        with _channel("GRPC_CALIFICACIONES_HOST", "GRPC_CALIFICACIONES_PORT") as ch:
            stub = calificaciones_pb2_grpc.CalificacionesServiceStub(ch)
            resp = stub.GetPromedioAlumno(calificaciones_pb2.PromedioRequest(materia_id=materia_id, alumno_id=alumno_id))
            return resp.promedio
    except Exception as e:
        logging.warning("[grpc_clients] get_promedio_alumno falló: %s", e)
        return 0.0


# ─── MS-5 Asistencias ────────────────────────────────────────────────────────
def get_estadisticas_asistencia(materia_id: str) -> list:
    if USE_FALLBACK or not PROTOS_OK:
        return [{"alumno_id": a["id"], "nombre": a["nombre"], "matricula": a["matricula"], "porcentaje": round(85 + i * 2, 1)} for i, a in enumerate(_DEMO_ALUMNOS)]
    try:
        with _channel("GRPC_ASISTENCIAS_HOST", "GRPC_ASISTENCIAS_PORT") as ch:
            stub = asistencias_pb2_grpc.AsistenciasServiceStub(ch)
            resp = stub.GetEstadisticasAsistencia(asistencias_pb2.EstadisticasRequest(materia_id=materia_id))
            return [{"alumno_id": a.alumno_id, "nombre": a.nombre, "matricula": a.matricula, "porcentaje": a.porcentaje} for a in resp.estadisticas]
    except Exception as e:
        logging.warning("[grpc_clients] get_estadisticas_asistencia falló: %s", e)
        return []


def get_asistencia_alumno(materia_id: str, alumno_id: str) -> dict:
    if USE_FALLBACK or not PROTOS_OK:
        return {"porcentaje": 88.0, "clases_asistidas": 22, "clases_totales": 25}
    try:
        with _channel("GRPC_ASISTENCIAS_HOST", "GRPC_ASISTENCIAS_PORT") as ch:
            stub = asistencias_pb2_grpc.AsistenciasServiceStub(ch)
            resp = stub.GetAsistenciaAlumno(asistencias_pb2.AsistenciaAlumnoRequest(materia_id=materia_id, alumno_id=alumno_id))
            return {"porcentaje": resp.porcentaje, "clases_asistidas": resp.clases_asistidas, "clases_totales": resp.clases_totales}
    except Exception as e:
        logging.warning("[grpc_clients] get_asistencia_alumno falló: %s", e)
        return {"porcentaje": 0.0, "clases_asistidas": 0, "clases_totales": 0}