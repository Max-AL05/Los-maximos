import grpc
import protos.auth_pb2 as auth_pb2
import protos.auth_pb2_grpc as auth_pb2_grpc
from django.conf import settings

class AuthClient:
    def __init__(self):
        # Se conecta al puerto del MS-1 (Auth)
        self.channel = grpc.insecure_channel(f"{settings.MS_AUTH_HOST}:50051")
        self.stub = auth_pb2_grpc.AuthServiceStub(self.channel)

    def validar_token(self, token):
        try:
            request = auth_pb2.ValidateTokenRequest(token=token)
            response = self.stub.ValidateToken(request)
            return response.is_valid, response.user_claims
        except grpc.RpcError:
            return False, None