"""
Servicers gRPC de MS-2 Periodos & Materias.

Implementan los métodos del contrato periodos.proto:
    - GetMateriaById
    - GetMateriasByDocente
    - GetPeriodoActivo
"""
# from protos import periodos_pb2, periodos_pb2_grpc
# from apps.materias.models import Materia
# from apps.periodos.models import Periodo


# class PeriodosServicer(periodos_pb2_grpc.PeriodosServiceServicer):
#     def GetMateriaById(self, request, context):
#         # TODO: Materia.objects.get(id=request.materia_id) -> MateriaInfo
#         return periodos_pb2.MateriaInfo()
#
#     def GetMateriasByDocente(self, request, context):
#         # TODO: filtrar por docente_id (y opcionalmente periodo_id)
#         return periodos_pb2.MateriasList()
#
#     def GetPeriodoActivo(self, request, context):
#         # TODO: Periodo.objects.get(activo=True)
#         return periodos_pb2.PeriodoInfo()
