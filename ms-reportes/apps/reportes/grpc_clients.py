from __future__ import annotations
import logging, os, sys
import grpc
from django.conf import settings

_BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _BASE)
sys.path.insert(0, os.path.join(_BASE, 'protos'))

try:
    from protos import periodos_pb2, periodos_pb2_grpc
    from protos import alumnos_pb2, alumnos_pb2_grpc
    from protos import calificaciones_pb2, calificaciones_pb2_grpc
    from protos import asistencias_pb2, asistencias_pb2_grpc
    PROTOS_OK = True
except ImportError as exc:
    logging.warning('[grpc_clients] protos no disponibles: %s', exc)
    PROTOS_OK = False

def _channel(key):
    return grpc.insecure_channel(settings.GRPC_TARGETS.get(key, 'localhost:50051'))

def get_materia(materia_id):
    if not PROTOS_OK: return {}
    try:
        with _channel('periodos') as ch:
            r = periodos_pb2_grpc.PeriodosServiceStub(ch).GetMateriaById(periodos_pb2.GetMateriaByIdRequest(materia_id=materia_id))
            return {'id': r.materia_id, 'nrc': r.nrc, 'clave': r.clave, 'nombre': r.nombre, 'seccion': r.seccion, 'periodo_id': r.periodo_id, 'horario': r.horario, 'estado': r.estado}
    except Exception as e:
        logging.warning('[grpc_clients] get_materia fallo: %s', e); return {}

def get_alumnos_by_materia(materia_id):
    if not PROTOS_OK: return []
    try:
        with _channel('alumnos') as ch:
            resp = alumnos_pb2_grpc.AlumnosServiceStub(ch).GetAlumnosByMateria(alumnos_pb2.GetAlumnosByMateriaRequest(materia_id=materia_id))
            return [{'alumno_id': a.alumno_id, 'nombre_completo': a.nombre_completo, 'matricula': a.matricula} for a in resp.alumnos]
    except Exception as e:
        logging.warning('[grpc_clients] get_alumnos_by_materia fallo: %s', e); return []

def get_materias_alumno(alumno_id):
    return []

def get_concentrado(materia_id):
    if not PROTOS_OK: return []
    try:
        with _channel('calificaciones') as ch:
            resp = calificaciones_pb2_grpc.CalificacionesServiceStub(ch).GetConcentrado(calificaciones_pb2.GetConcentradoRequest(materia_id=materia_id))
            return [{'matricula': c.matricula, 'nombre_completo': c.nombre_completo, 'promedio_real': c.promedio_real, 'promedio_redondeado': c.promedio_redondeado, 'estado': c.estado} for c in resp.alumnos]
    except Exception as e:
        logging.warning('[grpc_clients] get_concentrado fallo: %s', e); return []

def get_estadisticas_materia(materia_id):
    empty = {'total_alumnos': 0, 'aprobados': 0, 'reprobados': 0, 'promedio_grupal': 0.0, 'calificacion_maxima': 0.0, 'calificacion_minima': 0.0}
    if not PROTOS_OK: return empty
    try:
        with _channel('calificaciones') as ch:
            r = calificaciones_pb2_grpc.CalificacionesServiceStub(ch).GetEstadisticasMateria(calificaciones_pb2.GetEstadisticasMateriaRequest(materia_id=materia_id))
            return {'total_alumnos': r.total_alumnos, 'aprobados': r.aprobados, 'reprobados': r.reprobados, 'promedio_grupal': r.promedio_grupal, 'calificacion_maxima': r.calificacion_maxima, 'calificacion_minima': r.calificacion_minima}
    except Exception as e:
        logging.warning('[grpc_clients] get_estadisticas_materia fallo: %s', e); return empty

def get_promedio_alumno(materia_id, alumno_id):
    if not PROTOS_OK: return 0.0
    try:
        with _channel('calificaciones') as ch:
            r = calificaciones_pb2_grpc.CalificacionesServiceStub(ch).GetPromedioAlumno(calificaciones_pb2.GetPromedioAlumnoRequest(alumno_id=alumno_id, materia_id=materia_id))
            return r.promedio_real
    except Exception as e:
        logging.warning('[grpc_clients] get_promedio_alumno fallo: %s', e); return 0.0

def get_asistencia_alumno(alumno_id, materia_id):
    if not PROTOS_OK: return []
    try:
        with _channel('asistencias') as ch:
            resp = asistencias_pb2_grpc.AsistenciasServiceStub(ch).GetAsistenciaAlumno(asistencias_pb2.GetAsistenciaAlumnoRequest(alumno_id=alumno_id, materia_id=materia_id))
            return [{'estado': r.estado} for r in resp.asistencias]
    except Exception as e:
        logging.warning('[grpc_clients] get_asistencia_alumno fallo: %s', e); return []

def get_estadisticas_asistencia(materia_id):
    empty = {'total_sesiones': 0, 'total_asistencias': 0, 'total_retardos': 0, 'total_ausencias': 0, 'porcentaje_asistencia': 0.0}
    if not PROTOS_OK: return empty
    try:
        with _channel('asistencias') as ch:
            r = asistencias_pb2_grpc.AsistenciasServiceStub(ch).GetEstadisticasAsistencia(asistencias_pb2.GetEstadisticasAsistenciaRequest(materia_id=materia_id))
            return {'total_sesiones': r.total_sesiones, 'total_asistencias': r.total_asistencias, 'total_retardos': r.total_retardos, 'total_ausencias': r.total_ausencias, 'porcentaje_asistencia': r.porcentaje_asistencia}
    except Exception as e:
        logging.warning('[grpc_clients] get_estadisticas_asistencia fallo: %s', e); return empty
