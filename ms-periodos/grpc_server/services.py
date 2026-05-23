"""
Servicers gRPC de MS-2 Periodos & Materias.

Implementan los métodos del contrato periodos.proto:
    - GetMateriaById       → busca una materia por UUID
    - GetMateriasByDocente → lista materias de un docente (opcionalmente por periodo)
    - GetPeriodoActivo     → devuelve el periodo activo actual
"""
import grpc

from apps.materias.models import Materia
from apps.periodos.models import Periodo
from protos import periodos_pb2, periodos_pb2_grpc


def _materia_to_proto(m: Materia) -> periodos_pb2.MateriaInfo:
    return periodos_pb2.MateriaInfo(
        materia_id  = str(m.id),
        nrc         = m.nrc,
        nombre      = m.nombre,
        seccion     = m.seccion,
        clave       = m.clave,
        docente_id  = m.docente_id,
        horario     = m.horario,
        periodo_id  = str(m.periodo_id),
        estado      = m.estado,
    )


class PeriodosServicer(periodos_pb2_grpc.PeriodosServiceServicer):

    def GetMateriaById(self, request, context):
        try:
            materia = Materia.objects.select_related("periodo").get(id=request.materia_id)
            return _materia_to_proto(materia)
        except Materia.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Materia {request.materia_id} no encontrada")
            return periodos_pb2.MateriaInfo()
        except Exception:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Error interno al buscar la materia")
            return periodos_pb2.MateriaInfo()

    def GetMateriasByDocente(self, request, context):
        try:
            qs = Materia.objects.filter(docente_id=request.docente_id)

            if request.periodo_id:
                qs = qs.filter(periodo_id=request.periodo_id)
            else:
                # Sin periodo especificado: usar el periodo activo
                try:
                    periodo_activo = Periodo.objects.get(activo=True)
                    qs = qs.filter(periodo=periodo_activo)
                except Periodo.DoesNotExist:
                    pass

            return periodos_pb2.MateriasList(
                materias=[_materia_to_proto(m) for m in qs]
            )
        except Exception:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Error interno al listar materias del docente")
            return periodos_pb2.MateriasList()

    def GetPeriodoActivo(self, request, context):
        try:
            periodo = Periodo.objects.get(activo=True)
            return periodos_pb2.PeriodoInfo(
                periodo_id    = str(periodo.id),
                nombre        = periodo.nombre,
                fecha_inicio  = str(periodo.fecha_inicio),
                fecha_fin     = str(periodo.fecha_fin),
                plan_estudios = periodo.plan_estudios,
                activo        = periodo.activo,
            )
        except Periodo.DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("No hay ningún periodo activo")
            return periodos_pb2.PeriodoInfo()
        except Exception:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details("Error interno al obtener el periodo activo")
            return periodos_pb2.PeriodoInfo()