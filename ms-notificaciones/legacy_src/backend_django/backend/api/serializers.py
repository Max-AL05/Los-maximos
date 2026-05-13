from rest_framework import serializers
from .models import CustomUser
from .models import Mascota
from .models import MascotaEncontrada
from .models import Adopcion
from .models import Publicacion
from .models import Comentario
from .models import MascotaAdopcion
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ('id','nombre', 'apellido', 'fecha_nacimiento', 'genero','email', 'numero_celular','password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            nombre=validated_data.get('nombre', ''),
            apellido=validated_data.get('apellido', ''),
            fecha_nacimiento=validated_data.get('fecha_nacimiento', '1990-01-01'),
            genero=validated_data.get('genero', 'N'),
            numero_celular=validated_data.get('numero_celular', '0000000000'),
    )
        return user

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required = True)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

#define el serializador para la mascota automaticamente
class MascotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mascota
        fields = '__all__'

#define el serializador para mascota encontrada
class MascotaEncontradaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MascotaEncontrada
        fields = '__all__'

#Serializer para la mascota encontrada
class MascotaAdopcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MascotaAdopcion
        fields = '__all__'
        read_only_fields = ['usuario']

class AdopcionSerializer(serializers.ModelSerializer):
    mascota_adopcion = MascotaAdopcionSerializer(required=False, allow_null=True)
    mascota_encontrada = serializers.PrimaryKeyRelatedField(queryset=MascotaEncontrada.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Adopcion
        fields = ['id_adopcion', 'usuario', 'mascota_adopcion', 'mascota_encontrada']

    def validate(self, data):
        if not data.get('mascota_adopcion') and not data.get('mascota_encontrada'):
            raise serializers.ValidationError("Debes asociar una mascota en adopción o una mascota encontrada.")
        if data.get('mascota_adopcion') and data.get('mascota_encontrada'):
            raise serializers.ValidationError("Solo puedes asociar una mascota en adopción o una mascota encontrada, no ambas.")
        return data

    def create(self, validated_data):
        mascota_adopcion_data = validated_data.pop('mascota_adopcion', None)
        if mascota_adopcion_data:
            mascota_adopcion = MascotaAdopcion.objects.create(**mascota_adopcion_data)
            adopcion = Adopcion.objects.create(mascota_adopcion=mascota_adopcion, **validated_data)
        else:
            adopcion = Adopcion.objects.create(**validated_data)
        return adopcion


class ComentarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comentario
        fields = '__all__'

class PublicacionSerializer(serializers.ModelSerializer):
    mascotas = MascotaSerializer(many=True, read_only=True)
    mascotas_encontradas = MascotaEncontradaSerializer(many=True, read_only=True)
    mascotas_adopcion = MascotaAdopcionSerializer(many=True, read_only=True)
    comentarios = ComentarioSerializer(many=True, read_only=True)

    class Meta:
        model = Publicacion
        fields = '__all__'



