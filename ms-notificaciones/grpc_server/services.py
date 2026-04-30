"""
Servicers gRPC de MS-6 Notificaciones.

Implementan los métodos del contrato notificaciones.proto:
    - SendBienvenida
    - SendBajaNotif
    - SendCierreMateria
    - SendResetPassword

Reutilizan apps.notificaciones.services (misma lógica que REST).
"""
# from protos import notificaciones_pb2, notificaciones_pb2_grpc
# from apps.notificaciones import services


# class NotificacionesServicer(notificaciones_pb2_grpc.NotificacionesServiceServicer):
#     def SendBienvenida(self, request, context):
#         notif = services.enviar_bienvenida(
#             alumno_id=request.alumno_id,
#             materia_id=request.materia_id,
#             clave_unica=request.clave_unica,
#         )
#         return notificaciones_pb2.SendResponse(
#             success=notif.estado == "ENVIADO",
#             message=notif.error or "",
#             notificacion_id=str(notif.id),
#         )
#
#     def SendBajaNotif(self, request, context):
#         notif = services.enviar_baja(
#             alumno_id=request.alumno_id,
#             docente_id=request.docente_id,
#             materia_id=request.materia_id,
#         )
#         return notificaciones_pb2.SendResponse(success=notif.estado == "ENVIADO")
#
#     def SendCierreMateria(self, request, context):
#         services.enviar_cierre_materia(materia_id=request.materia_id)
#         return notificaciones_pb2.SendResponse(success=True)
#
#     def SendResetPassword(self, request, context):
#         notif = services.enviar_reset_password(
#             user_id=request.user_id, reset_link=request.reset_link,
#         )
#         return notificaciones_pb2.SendResponse(success=notif.estado == "ENVIADO")
