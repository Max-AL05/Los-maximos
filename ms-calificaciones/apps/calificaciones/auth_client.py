"""
Cliente gRPC hacia MS-1 Auth.

Llama a `ValidateToken` para verificar JWTs emitidos por MS-1.
"""
import logging

import grpc
from django.conf import settings

import protos.auth_pb2 as auth_pb2
import protos.auth_pb2_grpc as auth_pb2_grpc


logger = logging.getLogger(__name__)


class AuthClient:
    """
    Cliente sincrónico hacia MS-1.

    El canal se reusa entre llamadas (es thread-safe en grpcio).
    Cada llamada respeta GRPC_DEFAULT_TIMEOUT para no colgar la request
    HTTP entrante si MS-1 está caído.
    """

    def __init__(self, target: str | None = None, timeout: float | None = None):
        self.target = target or settings.GRPC_TARGETS["auth"]
        self.timeout = timeout if timeout is not None else settings.GRPC_DEFAULT_TIMEOUT
        # Canal *insecure* porque vivimos en la red interna de Docker.
        # Si en el futuro se exponen los gRPC fuera de la red, cambiar a
        # grpc.secure_channel con credenciales TLS.
        self.channel = grpc.insecure_channel(self.target)
        self.stub = auth_pb2_grpc.AuthServiceStub(self.channel)

    # ───────────────────────────── API pública ──────────────────────────────

    def validar_token(self, token: str):
        """
        Valida un JWT contra MS-1.

        Returns
        -------
        tuple[bool, auth_pb2.UserClaims | None]
            (is_valid, claims). Si la llamada gRPC falla por red/timeout,
            regresa (False, None) y el caller decide si responder 401 o 503.
        """
        try:
            request = auth_pb2.ValidateTokenRequest(token=token)
            # ValidateToken devuelve directamente UserClaims (NO un wrapper).
            # Antes el código hacía `response.user_claims`, lo cual no existe
            # en el contrato y causaba AttributeError → 500 a quien llamara.
            claims = self.stub.ValidateToken(request, timeout=self.timeout)
            return claims.is_valid, claims
        except grpc.RpcError as e:
            code = e.code() if hasattr(e, "code") else "unknown"
            logger.warning("[auth_client] ValidateToken falló (%s): %s", code, e)
            # Re-lanzamos el RpcError para que el middleware decida 401 vs 503.
            raise

    def __del__(self):
        try:
            self.channel.close()
        except Exception:
            pass