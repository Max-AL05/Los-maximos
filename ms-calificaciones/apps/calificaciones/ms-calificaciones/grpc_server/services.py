"""
Servicers gRPC de MS-4 Calificaciones.

Implementa los métodos de `proto/calificaciones.proto`:
    - GetConcentrado          – tabla completa de alumnos+promedio
    - GetPromedioAlumno       – un solo alumno
    - GetEstadisticasMateria  – métricas grupales

REGLAS:
    * Los nombres y matrículas de los alumnos se obtienen llamando a MS-3
      (NO se hardcodean ni se devuelven vacíos). Los consumidores —
      especialmente MS-7 Reportes — esperan estos campos llenos.
    * Cada método maneja sus propias excepciones y setea el código gRPC
      apropiado en el contexto. NUNCA un método llama a otro reusando el
      contexto: cada uno construye su propia respuesta.
"""
import logging
from decimal import Decimal, ROUND_HALF_UP

import grpc
from django.db.models import Avg, Max, Min

from apps.calificaciones.alumnos_client import AlumnosClient
from apps.calificaciones.models import Calificacion
from apps.calificaciones.services import (
    ESTATUS_APROBADO,
    ESTATUS_EN_RIESGO,
    ESTATUS_REPROBADO,
    calcular_estatus,
    redondeo_institucional,
)
from apps.ponderaciones.models import Ponderacion

import protos.calificaciones_pb2 as calificaciones_pb2
import protos.calificaciones_pb2_grpc as calificaciones_pb2_grpc


logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Helper – cálculo del promedio ponderado para 1 alumno.
# Se usa tanto en GetConcentrado como en GetPromedioAlumno; centralizado
# acá para que la fórmula viva en un solo lugar.
# ─────────────────────────────────────────────────────────────────────────────
def _promedio_ponderado(alumno_id: str, ponderaciones) -> Decimal:
    promedio = Decimal("0.00")
    for pond in ponderaciones:
        notas = Calificacion.objects.filter(
            alumno_id=alumno_id,
            actividad__ponderacion=pond,
        )
        if not notas.exists():
            continue
        prom_cat = notas.aggregate(Avg("valor"))["valor__avg"] or Decimal("0.00")
        promedio += (prom_cat * pond.porcentaje) / Decimal("100")
    return promedio


# ─────────────────────────────────────────────────────────────────────────────
# Servicer
# ─────────────────────────────────────────────────────────────────────────────
class CalificacionesServicer(calificaciones_pb2_grpc.CalificacionesServiceServicer):

    # ─────────────────── GetConcentrado ────────────────────
    def GetConcentrado(self, request, context):
        materia_id = request.materia_id
        try:
            ponderaciones = list(Ponderacion.objects.filter(materia_id=materia_id))
            if not ponderaciones:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(
                    f"No hay rúbrica configurada para la materia {materia_id}"
                )
                return calificaciones_pb2.GetConcentradoResponse()

            # 1 RPC a MS-3 para nombres y matrículas reales.
            ms3 = AlumnosClient()
            inscritos = ms3.obtener_alumnos_de_materia(materia_id, solo_activos=True)
            inscritos_idx = {a["alumno_id"]: a for a in inscritos}

            alumnos_proto = []
            for alumno_id, datos in inscritos_idx.items():
                promedio = _promedio_ponderado(alumno_id, ponderaciones)
                redondeado = redondeo_institucional(promedio)

                alumnos_proto.append(calificaciones_pb2.AlumnoCalif(
                    alumno_id=alumno_id,
                    matricula=datos["matricula"],
                    nombre_completo=datos["nombre_completo"],
                    promedio_real=float(promedio),
                    promedio_redondeado=redondeado,
                    estatus=calcular_estatus(redondeado),
                ))

            return calificaciones_pb2.GetConcentradoResponse(alumnos=alumnos_proto)

        except Exception as e:
            logger.exception("GetConcentrado falló para materia=%s", materia_id)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error interno calculando concentrado: {e}")
            return calificaciones_pb2.GetConcentradoResponse()

    # ─────────────────── GetPromedioAlumno ────────────────────
    def GetPromedioAlumno(self, request, context):
        materia_id = request.materia_id
        alumno_id = request.alumno_id
        try:
            ponderaciones = list(Ponderacion.objects.filter(materia_id=materia_id))
            if not ponderaciones:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(
                    f"No hay rúbrica configurada para la materia {materia_id}"
                )
                return calificaciones_pb2.GetPromedioAlumnoResponse()

            promedio = _promedio_ponderado(alumno_id, ponderaciones)
            redondeado = redondeo_institucional(promedio)

            return calificaciones_pb2.GetPromedioAlumnoResponse(
                alumno_id=alumno_id,
                materia_id=materia_id,
                promedio_real=float(promedio),
                promedio_redondeado=redondeado,
            )

        except Exception as e:
            logger.exception(
                "GetPromedioAlumno falló para materia=%s alumno=%s",
                materia_id, alumno_id,
            )
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error interno: {e}")
            return calificaciones_pb2.GetPromedioAlumnoResponse()

    # ─────────────────── GetEstadisticasMateria ────────────────────
    def GetEstadisticasMateria(self, request, context):
        materia_id = request.materia_id
        try:
            ponderaciones = list(Ponderacion.objects.filter(materia_id=materia_id))
            if not ponderaciones:
                # Materia sin rúbrica: regresa estadísticas vacías con OK.
                # No es un error fatal — simplemente no hay nada que medir.
                return calificaciones_pb2.GetEstadisticasMateriaResponse(materia_id=materia_id)

            ms3 = AlumnosClient()
            inscritos = ms3.obtener_alumnos_de_materia(materia_id, solo_activos=True)

            promedios: list[Decimal] = []
            aprobados = en_riesgo = reprobados = 0

            for alumno in inscritos:
                p = _promedio_ponderado(alumno["alumno_id"], ponderaciones)
                redondeado = redondeo_institucional(p)
                estatus = calcular_estatus(redondeado)
                if estatus == ESTATUS_APROBADO:
                    aprobados += 1
                elif estatus == ESTATUS_EN_RIESGO:
                    en_riesgo += 1
                else:
                    reprobados += 1
                promedios.append(p)

            # Métricas de grupo. Si ningún alumno tiene promedio (porque no
            # hay calificaciones cargadas todavía), regresamos ceros.
            if promedios:
                # Calculamos sobre los promedios ponderados, no sobre la
                # tabla cruda de notas — antes hacía Avg sobre `valor` lo
                # cual mezclaba escalas distintas (10/10 examen vs 10/10 tarea
                # contaban igual aunque la rúbrica les diera pesos distintos).
                prom_grupal = sum(promedios) / Decimal(len(promedios))
                cal_max = max(promedios)
                cal_min = min(promedios)
            else:
                prom_grupal = cal_max = cal_min = Decimal("0.00")

            return calificaciones_pb2.GetEstadisticasMateriaResponse(
                materia_id=materia_id,
                total_alumnos=len(inscritos),
                aprobados=aprobados,
                reprobados=reprobados,
                en_riesgo=en_riesgo,
                promedio_grupal=float(prom_grupal),
                calificacion_maxima=float(cal_max),
                calificacion_minima=float(cal_min),
            )

        except Exception as e:
            logger.exception("GetEstadisticasMateria falló para materia=%s", materia_id)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error interno: {e}")
            return calificaciones_pb2.GetEstadisticasMateriaResponse(materia_id=materia_id)