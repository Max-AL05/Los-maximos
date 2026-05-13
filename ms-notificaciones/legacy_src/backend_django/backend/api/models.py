from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.db import models
from django.utils.timezone import now
now
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El Email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
   #Opciones de género
    GENERO_CHOICES = [
        ('F', 'Femenino'),
        ('M', 'Masculino'),
        ('N', 'Prefiero no decirlo')
    ]
    id=models.AutoField(primary_key=True)
    username = None
    nombre = models.CharField(max_length=100, default='NombreDesconocido')
    apellido=models.CharField(max_length=100,default='ApellidoDesconocido')
    fecha_nacimiento=models.DateField(default='1990-01-01')
    genero = models.CharField(
        max_length=1,
        choices=GENERO_CHOICES,
        default='N', # Opción por defecto: prefiero no decirlo
    )
    email = models.EmailField('email address', unique=True)
    numero_celular=models.CharField(max_length=15, default='0000000000')
    fecha_registro=models.DateTimeField(auto_now_add=True) #Fecha de registro al momento de crear el usuario
    ultima_actualizacion=models.DateTimeField(auto_now=True) #Fecha de la última actualización al momento de crear el usuario

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre','apellido','fecha_nacimiento','genero','numero_celular']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    def save(self, *args, **kwargs):
        # Asegura que la contraseña esté hasheada antes de guardar
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            self.set_password(self.password)
        super().save(*args, **kwargs)

#Modelo para registrar mascotas perdidas
class Mascota(models.Model):
    ESPECIE_CHOICES = [
        ('perro', 'Perro'),
        ('gato', 'Gato'),
        ('ave', 'Ave'),
        ('conejo', 'Conejo'),
        ('otro', 'Otro'),
    ]
    SEXO_CHOICES = [
        ('macho', 'Macho'),
        ('hembra', 'Hembra'),
        ('desconocido', 'No lo sé'),
    ]

    id_mascota = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='mascotas')
    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=20, choices=ESPECIE_CHOICES)
    otra_especie = models.CharField(max_length=100, blank=True)  # Solo si especie == 'otro'
    raza = models.CharField(max_length=100, blank=True)
    edad = models.PositiveIntegerField(null=True, blank=True)
    unidad_edad = models.CharField(max_length=20, blank=True)  # año(s), mes(es), semana(s)
    sexo = models.CharField(max_length=20, choices=SEXO_CHOICES)
    color_principal = models.CharField(max_length=50, blank=True)
    caracteristicas_especiales = models.TextField(blank=True)
    fecha_perdida = models.DateField(null=True, blank=True)
    lugar_perdida = models.CharField(max_length=255, blank=True)
    ultima_vez = models.TextField(blank=True)
    telefono = models.CharField(max_length=20)
    notas_adicionales = models.TextField(blank=True)
    fotos = models.ImageField(upload_to='mascotas_fotos/', blank=True, null=True)  # Para una sola foto. Para varias, usa un modelo aparte.

    def __str__(self):
        return f"{self.nombre} ({self.especie})"

#Modelo para mascotas encontradas
class MascotaEncontrada(models.Model):
    ESPECIE_CHOICES = [
        ('perro', 'Perro'),
        ('gato', 'Gato'),
        ('otro', 'Otro'),
    ]
    SEXO_CHOICES = [
        ('M', 'Macho'),
        ('H', 'Hembra'),
        ('D', 'Desconocido'),
    ]
    ESTADO_PUBLICACION_CHOICES = [
        ('encontrado', 'Encontrado'),
        ('adopcion', 'En adopción'),
        ('otro', 'Otro'),
    ]

    id_mascota_encontrada = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='mascotas_encontradas')
    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=20, choices=ESPECIE_CHOICES)
    raza = models.CharField(max_length=100, blank=True)
    edad = models.PositiveIntegerField(null=True, blank=True)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    color = models.CharField(max_length=50, blank=True)
    tamaño = models.CharField(max_length=50, blank=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    ultima_ubicacion = models.CharField(max_length=255, blank=True)
    fecha_encontrada = models.DateField(null=True, blank=True)
    senas_particulares = models.TextField(blank=True)
    estado_publicacion = models.CharField(max_length=20, choices=ESTADO_PUBLICACION_CHOICES)
    contacto = models.CharField(max_length=100, blank=True)
    recompensa = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fotos = models.ImageField(upload_to='mascotas_encontradas_fotos/', blank=True, null=True)
    id_adopcion = models.ForeignKey('Adopcion', on_delete=models.SET_NULL, null=True, blank=True, related_name='mascotas_encontradas')

    def __str__(self):
        return f"{self.nombre} ({self.especie})"

#Modelo para registrar adopciones
class Adopcion(models.Model):
    id_adopcion = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='adopciones')
    mascota_adopcion = models.ForeignKey('MascotaAdopcion', on_delete=models.CASCADE, related_name='adopciones', null=True, blank=True)
    mascota_encontrada = models.ForeignKey('MascotaEncontrada', on_delete=models.CASCADE, related_name='adopciones', null=True, blank=True)

    def clean(self):
        if not self.mascota_adopcion and not self.mascota_encontrada:
            raise ValidationError("Debes asociar una mascota en adopción o una mascota encontrada.")
        if self.mascota_adopcion and self.mascota_encontrada:
            raise ValidationError("Solo puedes asociar una mascota en adopción o una mascota encontrada, no ambas.")

    def __str__(self):
        return f"Adopción {self.id_adopcion} - Usuario {self.usuario.id}"

#Modelo para publicaciones
class Publicacion(models.Model):
    TIPO_CHOICES = [
        ('adopcion', 'Adopción'),
        ('busqueda', 'Búsqueda'),
        ('encontrada', 'Mascota Encontrada'),
    ]
    ESTADO_CHOICES = [
        ('vigente', 'Vigente'),
        ('finalizado', 'Finalizado'),
    ]

    id_publicacion = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='publicaciones')
    mascotas = models.ManyToManyField(Mascota, blank=True, related_name='publicaciones')
    mascotas_encontradas = models.ManyToManyField(MascotaEncontrada, blank=True, related_name='publicaciones_encontradas')
    mascotas_adopcion = models.ManyToManyField('MascotaAdopcion', blank=True, related_name='publicaciones_adopcion')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='vigente')
    contenido = models.TextField()
    reacciones = models.PositiveIntegerField(default=0)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Publicación {self.id_publicacion} - {self.tipo}"

#Modelo para comentario
class Comentario(models.Model):
    id_comentario = models.AutoField(primary_key=True)
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comentarios')
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentario {self.id_comentario} en Publicación {self.publicacion.id_publicacion}"

#Modelo para mensajes
class Mensaje(models.Model):
    id_mensaje = models.AutoField(primary_key=True)
    emisor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='mensajes_enviados')
    receptor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='mensajes_recibidos')
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    def __str__(self):
        return f"Mensaje de {self.emisor} a {self.receptor}"

#Modelo para notificaciones
class Notificacion(models.Model):
    id_notificacion = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notificaciones')
    mensaje = models.CharField(max_length=255)
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notificación para {self.usuario}"

#Modelo para reacciones
class Reaccion(models.Model):
    id_reaccion = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reacciones')
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, related_name='reacciones_obj')  # Cambiado aquí
    tipo = models.CharField(max_length=20, default='me_encanta')  # Solo "me_encanta" por ahora
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'publicacion')  # Un usuario solo puede reaccionar una vez por publicación

    def __str__(self):
        return f"{self.usuario} reaccionó a {self.publicacion}"

#Modelo para mascota adopcion
class MascotaAdopcion(models.Model):
    id_mascota_adopcion = models.AutoField(primary_key=True)
    usuario = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='mascotas_adopcion')
    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=20)
    raza = models.CharField(max_length=100, blank=True)
    edad = models.CharField(max_length=50)
    tamanio = models.CharField(max_length=50)
    sexo = models.CharField(max_length=20)
    descripcion = models.TextField()
    ubicacion = models.CharField(max_length=255)
    vacunado = models.BooleanField(default=False)
    esterilizado = models.BooleanField(default=False)
    amigableConMascotas = models.BooleanField(default=False)
    amigableConNinos = models.BooleanField(default=False)
    necesidadesEspeciales = models.TextField(blank=True)
    foto = models.ImageField(upload_to='mascotas_adopcion_fotos/', blank=True, null=True)
    contactoNombre = models.CharField(max_length=100)
    contactoEmail = models.EmailField()
    contactoTelefono = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nombre} ({self.especie})"
