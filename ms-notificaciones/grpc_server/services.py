"""
Servicers gRPC de MS-6 Notificaciones.

Implementan los métodos del contrato proto/notificaciones.proto.
Reutilizan apps.notificaciones.services (misma lógica que REST).

Activar cuando hayas generado los stubs con:
    bash scripts/generate_protos.sh
"""
# from protos import notificaciones_pb2, notificaciones_pb2_grpc
# from apps.notificaciones import services


# class NotificacionesServicer(notificaciones_pb2_grpc.NotificacionesServiceServicer):
#     def SendBienvenida(self, request, context):
#         notif = services.enviar_bienvenida(
#             alumno_id=request.alumno_id,
#             alumno_email=request.alumno_email,
#             alumno_nombre=request.alumno_nombre,
#             materia_id=request.materia_id,
#             materia_nombre=request.materia_nombre,
#             clave_unica=request.clave_unica,
#         )
#         return notificaciones_pb2.SendResponse(
#             success=notif.estado == "ENVIADO",
#             message=notif.error or "",
#             notificacion_id=str(notif.id),
#         )
#
#     def SendBajaNotif(self, request, context):
#         notif = services.enviar_baja(...)
#         return notificaciones_pb2.SendResponse(success=notif.estado == "ENVIADO")
#
#     def SendCierreMateria(self, request, context):
#         services.enviar_cierre_materia(...)
#         return notificaciones_pb2.SendResponse(success=True)
#
#     def SendResetPassword(self, request, context):
#         notif = services.enviar_reset_password(...)
#         return notificaciones_pb2.SendResponse(success=notif.estado == "ENVIADO")
