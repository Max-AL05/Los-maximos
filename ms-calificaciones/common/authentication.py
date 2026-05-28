from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import jwt
import os


class StatelessJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ', 1)[1]
        secret = os.environ.get('JWT_SECRET_KEY', '')
        algorithm = os.environ.get('JWT_ALGORITHM', 'HS256')

        try:
            payload = jwt.decode(token, secret, algorithms=[algorithm])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expirado.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Token inválido.')

        return (StatelessUser(payload), token)


class StatelessUser:
    def __init__(self, payload: dict):
        self.id        = payload.get('sub') or payload.get('user_id', '')
        self.email     = payload.get('email', '')
        self.role      = payload.get('role', '')
        self.is_active = True
        self.is_staff  = self.role == 'ADMIN'
        self.pk        = self.id

    @property
    def is_authenticated(self): return True

    @property
    def is_anonymous(self): return False

    def __str__(self): return self.email