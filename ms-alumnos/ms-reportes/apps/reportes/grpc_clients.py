"""
Cliente gRPC para llamar a los demás microservicios (MS-2 / MS-3 / MS-4 / MS-5).

Cada función hace UN intento por gRPC y, si falla (o si USE_FALLBACK = True),
devuelve datos demo para que la presentación pueda correr aunque los demás
MS aún no estén levantados.

IMPORTANTE: los nombres de mensajes y los órdenes de campos siguen los
contratos en /proto/*.proto del repo. Si cambian los .proto, hay que
regenerar los pb2 y revisar este archivo.
"""
from __future__ import annotations

import logging
import os
import sys
import grpc
from django.conf import settings

# Agregar la raíz del proyecto al path para que los pb2_grpc.py encuentren
# sus pares (pb2.py) en la misma carpeta.
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


# ───────────────────────── Configuración de fallback ────────────────────────
# Cambiar a False cuando los demás MS estén corriendo. En False, los errores
# de gRPC se propagan (más honesto para la entrega final). En True, cualquier
# fallo silenciosamente cae a los datos demo de abajo.
USE_FALLBACK = True


# ───────────────────────────── Datos demo ──────────────────────────────────
# Cubren TODOS los campos que `services.py` lee con .get(). Si falta un campo
# aquí, sale vacío en el reporte (eso fue el bug original).
_DEMO_MATERIA = {
    "id": "demo-001",
    "nrc": "48308",
    "clave": "ITIS 260",
    "nombre": "Desarrollo de Sitios Web",
    "seccion": "001",
    "periodo_id": "primavera-2026",
    "estado": "ABIERTA",
    "horario": "L 1500-1559, M 1500-1659, V 1500-1659",
}

_DEMO_ALUMNOS = [
    {"id": "001", "alumno_id": "001", "nombre": "AGUILAR SALDIVAR ANGEL G.",
     "nombre_completo": "AGUILAR SALDIVAR, ANGEL G.",    "matricula": "202224429"},
    {"id": "002", "alumno_id": "002", "nombre": "AMADOR LAGUNES ALEJANDRO",
     "nombre_completo": "AMADOR LAGUNES, ALEJANDRO",     "matricula": "202213377"},
    {"id": "003", "alumno_id": "003", "nombre": "AVENDAÑO VEGA ERWIN G.",
     "nombre_completo": "AVENDAÑO VEGA, ERWIN G.",       "matricula": "202220926"},
    {"id": "004", "alumno_id": "004", "nombre": "CONTRERAS GONZALEZ GERSON E.",
     "nombre_completo": "CONTRERAS GONZALEZ, GERSON E.", "matricula": "202237583"},
    {"id": "005", "alumno_id": "005", "nombre": "ESCUDERO RIVERA ALFREDO",
     "nombre_completo": "ESCUDERO RIVERA, ALFREDO",      "matricula": "202222184"},
]

# Promedios diversos (no todo aprobado) para que el reporte demuestre los
# dos estilos visuales (verde APROBADO / rojo REPROBADO).
_DEMO_PROMEDIOS = [8.7, 7.2, 9.4, 5.8, 8.1]


def _redondear(p: float) -> int:
    """>= 0.5 sube al entero superior; < 0.5 baja al inferior (regla del rúbrico)."""
    entero = int(p)
    return entero + 1 if (p - entero) >= 0.5 else entero


# ─────────────────────────────── Canales ───────────────────────────────────
def _channel(target_key: str):
    """Construye un canal gRPC inseguro a `settings.GRPC_TARGETS[target_key]`."""
    target = settings.GRPC_TARGETS.get(target_key, "localhost:50051")
    return grpc.insecure_channel(target)


# ════════════════════════════════════════════════════════════════════════════
#  MS-2  Periodos & Materias
# ════════════════════════════════════════════════════════════════════════════
def get_materia_by_id(materia_id: str) -> dict:
    if USE_FALLBACK or not PROTOS_OK:
        return dict(_DEMO_MATERIA)
    try:
        with _channel("periodos") as ch:
            stub = periodos_pb2_grpc.PeriodosServiceStub(ch)
            req = periodos_pb2.GetMateriaByIdRequest(materia_id=materia_id)
            r = stub.GetMateriaById(req)
            return {
                "id": r.id,
                "nrc": r.nrc,
                "clave": r.clave,
                "nombre": r.nombre,
                "seccion": r.seccion,
                "periodo_id": r.periodo_id,
                "estado": r.estado,
                "horario": r.horario,
            }
    except Exception as e:
        logging.warning("[grpc_clients] get_materia_by_id falló: %s", e)
        if USE_FALLBACK:
            return dict(_DEMO_MATERIA)
        raise


# ════════════════════════════════════════════════════════════════════════════
#  MS-3  Docentes & Alumnos
# ════════════════════════════════════════════════════════════════════════════
def get_alumnos_by_materia(materia_id: str) -> list[dict]:
    if USE_FALLBACK or not PROTOS_OK:
        return [dict(a) for a in _DEMO_ALUMNOS]
    try:
        with _channel("alumnos") as ch:
            stub = alumnos_pb2_grpc.AlumnosServiceStub(ch)
            req = alumnos_pb2.GetAlumnosByMateriaRequest(materia_id=materia_id)
            r = stub.GetAlumnosByMateria(req)
            return [
                {
                    "id": a.alumno_id,
                    "alumno_id": a.alumno_id,
                    "nombre": a.nombre_completo,
                    "nombre_completo": a.nombre_completo,
                    "matricula": a.matricula,
                }
                for a in r.alumnos
            ]
    except Exception as e:
        logging.warning("[grpc_clients] get_alumnos_by_materia falló: %s", e)
        if USE_FALLBACK:
            return [dict(a) for a in _DEMO_ALUMNOS]
        raise


def get_materias_alumno(alumno_id: str) -> list[dict]:
    """No hay un rpc directo en el .proto de alumnos. Si se necesita,
    se emula consultando IsAlumnoEnMateria por cada materia conocida.
    En fallback devuelve la materia demo."""
    if USE_FALLBACK or not PROTOS_OK:
        return [dict(_DEMO_MATERIA)]
    # Si en el futuro se agrega GetMateriasByAlumno al proto, implementar aquí.
    logging.info("[grpc_clients] get_materias_alumno: no hay rpc, devolviendo demo")
    return [dict(_DEMO_MATERIA)]


# ════════════════════════════════════════════════════════════════════════════
#  MS-4  Calificaciones & Ponderaciones
# ════════════════════════════════════════════════════════════════════════════
def get_concentrado_calificaciones(materia_id: str) -> list[dict]:
    if USE_FALLBACK or not PROTOS_OK:
        out = []
        for alu, p in zip(_DEMO_ALUMNOS, _DEMO_PROMEDIOS):
            redon = _redondear(p)
            out.append({
                "alumno_id": alu["alumno_id"],
                "matricula": alu["matricula"],
                "nombre": alu["nombre"],
                "nombre_completo": alu["nombre_completo"],
                "promedio": p,
                "promedio_real": p,
                "promedio_redondeado": redon,
                "estado": "APROBADO" if redon >= 6 else "REPROBADO",
            })
        return out
    try:
        with _channel("calificaciones") as ch:
            stub = calificaciones_pb2_grpc.CalificacionesServiceStub(ch)
            req = calificaciones_pb2.GetConcentradoRequest(materia_id=materia_id)
            r = stub.GetConcentrado(req)
            out = []
            for c in r.alumnos:
                redon = _redondear(c.promedio_real)
                out.append({
                    "alumno_id": c.alumno_id,
                    "matricula": c.matricula,
                    "nombre": c.nombre_completo,
                    "nombre_completo": c.nombre_completo,
                    "promedio": c.promedio_real,
                    "promedio_real": c.promedio_real,
                    "promedio_redondeado": redon,
                    "estado": "APROBADO" if redon >= 6 else "REPROBADO",
                })
            return out
    except Exception as e:
        logging.warning("[grpc_clients] get_concentrado_calificaciones falló: %s", e)
        if USE_FALLBACK:
            return get_concentrado_calificaciones(materia_id)  # cae a fallback de arriba
        raise


def get_promedio_alumno(materia_id: str, alumno_id: str) -> float:
    if USE_FALLBACK or not PROTOS_OK:
        return 8.5
    try:
        with _channel("calificaciones") as ch:
            stub = calificaciones_pb2_grpc.CalificacionesServiceStub(ch)
            req = calificaciones_pb2.GetPromedioAlumnoRequest(
                materia_id=materia_id, alumno_id=alumno_id,
            )
            r = stub.GetPromedioAlumno(req)
            return r.promedio
    except Exception as e:
        logging.warning("[grpc_clients] get_promedio_alumno falló: %s", e)
        if USE_FALLBACK:
            return 8.5
        raise


def get_estadisticas_materia_resumen(materia_id: str) -> dict:
    """Resumen del concentrado: total/aprobados/reprobados/promedio/máx/mín.
    Lo derivamos del concentrado para no duplicar lógica."""
    alumnos = get_concentrado_calificaciones(materia_id)
    if not alumnos:
        return {
            "total_alumnos": 0,
            "aprobados": 0,
            "reprobados": 0,
            "promedio_grupal": 0.0,
            "calificacion_maxima": 0.0,
            "calificacion_minima": 0.0,
        }
    promedios = [a["promedio_real"] for a in alumnos]
    aprobados = sum(1 for a in alumnos if a["estado"] == "APROBADO")
    return {
        "total_alumnos": len(alumnos),
        "aprobados": aprobados,
        "reprobados": len(alumnos) - aprobados,
        "promedio_grupal": round(sum(promedios) / len(promedios), 2),
        "calificacion_maxima": max(promedios),
        "calificacion_minima": min(promedios),
    }


# ════════════════════════════════════════════════════════════════════════════
#  MS-5  Asistencias QR
# ════════════════════════════════════════════════════════════════════════════
def get_asistencia_alumno(alumno_id: str, materia_id: str) -> list[dict]:
    """Lista de registros de asistencia del alumno en la materia.
    Cada registro: {asistencia_id, fecha, estado, sesion_id}.
    Estados: PRESENTE | RETARDO | AUSENTE.
    """
    if USE_FALLBACK or not PROTOS_OK:
        # Demo: 25 sesiones, mezcla de estados para mostrar las 3 columnas.
        # Determinístico por alumno_id (mismo alumno = mismo set).
        seed = sum(ord(c) for c in str(alumno_id)) or 1
        regs = []
        for i in range(25):
            ix = (seed + i) % 10
            estado = ("PRESENTE" if ix < 7 else
                      "RETARDO" if ix < 9 else
                      "AUSENTE")
            regs.append({
                "asistencia_id": f"a-{alumno_id}-{i}",
                "fecha": f"2026-{2 + i // 10:02d}-{1 + i % 28:02d}",
                "estado": estado,
                "sesion_id": f"s-{i}",
            })
        return regs
    try:
        with _channel("asistencias") as ch:
            stub = asistencias_pb2_grpc.AsistenciasServiceStub(ch)
            req = asistencias_pb2.GetAsistenciaAlumnoRequest(
                alumno_id=alumno_id, materia_id=materia_id,
            )
            r = stub.GetAsistenciaAlumno(req)
            return [
                {
                    "asistencia_id": a.asistencia_id,
                    "fecha": a.fecha,
                    "estado": a.estado,
                    "sesion_id": a.sesion_id,
                }
                for a in r.asistencias
            ]
    except Exception as e:
        logging.warning("[grpc_clients] get_asistencia_alumno falló: %s", e)
        if USE_FALLBACK:
            return get_asistencia_alumno(alumno_id, materia_id)  # demo
        raise


def get_asistencia_alumno_resumen(alumno_id: str, materia_id: str) -> dict:
    """Resumen porcentaje/asistidas/totales para el endpoint de estadísticas.
    Se calcula a partir de la lista de registros."""
    regs = get_asistencia_alumno(alumno_id, materia_id)
    total = len(regs)
    asistidas = sum(1 for r in regs if r["estado"] in ("PRESENTE", "RETARDO"))
    pct = round(asistidas / total * 100, 1) if total else 0.0
    return {
        "porcentaje": pct,
        "clases_asistidas": asistidas,
        "clases_totales": total,
    }


def get_estadisticas_asistencia(materia_id: str) -> dict:
    """Resumen grupal de asistencias para una materia."""
    if USE_FALLBACK or not PROTOS_OK:
        return {
            "total_sesiones": 25,
            "total_asistencias": 110,
            "total_retardos": 9,
            "total_ausencias": 6,
            "porcentaje_asistencia": 95.2,
        }
    try:
        with _channel("asistencias") as ch:
            stub = asistencias_pb2_grpc.AsistenciasServiceStub(ch)
            req = asistencias_pb2.GetEstadisticasAsistenciaRequest(materia_id=materia_id)
            r = stub.GetEstadisticasAsistencia(req)
            return {
                "total_sesiones": r.total_sesiones,
                "total_asistencias": r.total_asistencias,
                "total_retardos": r.total_retardos,
                "total_ausencias": r.total_ausencias,
                "porcentaje_asistencia": round(r.porcentaje_asistencia, 1),
            }
    except Exception as e:
        logging.warning("[grpc_clients] get_estadisticas_asistencia falló: %s", e)
        if USE_FALLBACK:
            return get_estadisticas_asistencia(materia_id)
        raise


# ─── Aliases que ya usaba services.py ───────────────────────────────────────
get_materia = get_materia_by_id
get_concentrado = get_concentrado_calificaciones
get_estadisticas_materia = get_estadisticas_materia_resumen