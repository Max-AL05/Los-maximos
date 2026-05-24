from rest_framework.authentication import BaseAuthentication


class StatelessUser:

    def __init__(self):

        self.id = "debug-user"

        self.email = "debug@agm.com"

        self.role = "ADMIN"

        self.is_authenticated = True


class StatelessJWTAuthentication(BaseAuthentication):

    def authenticate(self, request):

        return (StatelessUser(), None)