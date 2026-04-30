"""
Servicers gRPC de MS-1 Auth & Users.

Implementan los métodos del contrato auth.proto:
    - ValidateToken
    - GetUserById
    - CheckRole
"""
# Una vez generados los stubs (bash scripts/generate_protos.sh):
# from protos import auth_pb2, auth_pb2_grpc


# class AuthServicer(auth_pb2_grpc.AuthServiceServicer):
#     def ValidateToken(self, request, context):
#         # TODO: decodificar JWT con SIMPLE_JWT['SIGNING_KEY']
#         #       devolver UserClaims(user_id, email, role, is_valid, exp)
#         return auth_pb2.UserClaims(is_valid=False)
#
#     def GetUserById(self, request, context):
#         # TODO: User.objects.get(id=request.user_id)
#         return auth_pb2.UserProfile()
#
#     def CheckRole(self, request, context):
#         # TODO: User.objects.filter(id=request.user_id, role=request.role).exists()
#         return auth_pb2.CheckRoleResponse(has_role=False)
