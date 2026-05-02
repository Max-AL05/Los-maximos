"""Serializers de MS-1 Auth & Users."""
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer # type: ignore

from .models import User, Role


class RegisterSerializer(serializers.ModelSerializer):
    """
    Crea un usuario con cualquier rol.

    En producción este endpoint debería estar restringido a Administradores
    (para crear otros admins/docentes) y los alumnos se crean automáticamente
    desde MS-3 al importar el Excel de la materia. Para desarrollo está abierto.
    """
    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "role",
            "nombre_completo",
            "matricula",
            "cubiculo",
        )
        read_only_fields = ("id",)

    def validate_role(self, value):
        if value not in Role.values:
            raise serializers.ValidationError(f"Rol inválido. Usar uno de: {Role.values}")
        return value

    def validate(self, attrs):
        role = attrs.get("role")
        if role == Role.ALUMNO and not attrs.get("matricula"):
            raise serializers.ValidationError(
                {"matricula": "La matrícula es obligatoria para alumnos."}
            )
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Login que retorna un JWT con el `role` y datos del usuario embebidos.

    Esto permite que otros microservicios validen permisos sin tener que
    llamar al MS-1 cada vez (basta con verificar la firma del token).
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Custom claims que viajarán DENTRO del JWT
        token["role"] = user.role
        token["email"] = user.email
        token["nombre_completo"] = user.nombre_completo
        return token

    def validate(self, attrs):
        # Genera access + refresh
        data = super().validate(attrs)
        # Adjunta info del usuario en la respuesta también (útil para el frontend)
        data["user"] = {
            "id": str(self.user.id),
            "email": self.user.email,
            "role": self.user.role,
            "nombre_completo": self.user.nombre_completo,
            "matricula": self.user.matricula,
            "cubiculo": self.user.cubiculo,
        }
        return data


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, write_only=True)


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "nombre_completo",
            "role",
            "matricula",
            "cubiculo",
            "is_active",
            "date_joined",
        )
        read_only_fields = fields
