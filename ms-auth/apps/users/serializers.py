from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer # type: ignore

from .models import User, Role


class RegisterSerializer(serializers.ModelSerializer):

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

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["email"] = user.email
        token["nombre_completo"] = user.nombre_completo
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
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
