# MS-6 Notificaciones (AGM)

Microservicio de notificaciones por email del sistema AGM.

- **Stack:** Django 5 + DRF + PostgreSQL 16
- **REST:** puerto `8006`
- **gRPC:** puerto `50056` (placeholder, se activa cuando generes los stubs)
- **Tipos soportados:** `BIENVENIDA`, `BAJA`, `CIERRE_MATERIA`, `RESET_PASSWORD`

---

## Estructura

```
ms-notificaciones/
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.standalone.yml
├── .env.example
├── config/                       # Configuracion Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   └── notificaciones/
│       ├── models.py             # Modelo Notificacion
│       ├── serializers.py        # Validacion REST
│       ├── views.py              # Endpoints
│       ├── urls.py
│       ├── services.py           # Logica de negocio
│       ├── admin.py
│       └── templates/emails/     # Plantillas HTML
│           ├── bienvenida.html
│           ├── baja.html
│           ├── cierre_materia.html
│           └── reset_password.html
├── grpc_server/                  # Servidor gRPC (placeholder)
│   ├── server.py
│   └── services.py
└── postman/
    └── ms-notificaciones.postman_collection.json
```

---

## PASO A PASO

### Opcion A: con Docker (recomendado, mas facil)

```bash
# 1. Copiar variables de entorno
cp .env.example .env

# 2. Levantar todo (ms + postgres)
docker-compose -f docker-compose.standalone.yml up --build
```

Listo. El servicio queda en `http://localhost:8006`.

### Opcion B: local (sin Docker)

#### 1) Crear y activar entorno virtual

```bash
python -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate            # Windows
```

#### 2) Instalar dependencias

```bash
pip install -r requirements.txt
```

#### 3) Levantar PostgreSQL local y crear la base

```bash
# Si tienes Postgres instalado:
psql -U postgres -c "CREATE USER agm_user WITH PASSWORD 'agm_password';"
psql -U postgres -c "CREATE DATABASE agm_notif_db OWNER agm_user;"
```

O bien, levanta solo Postgres con Docker:

```bash
docker run -d --name pg-notif \
  -e POSTGRES_DB=agm_notif_db \
  -e POSTGRES_USER=agm_user \
  -e POSTGRES_PASSWORD=agm_password \
  -p 5432:5432 \
  postgres:16-alpine
```

#### 4) Configurar variables de entorno

```bash
cp .env.example .env
# Edita .env si necesitas cambiar algo. Por defecto:
# - EMAIL_BACKEND=console (los correos se imprimen en la terminal)
# - DB_HOST=localhost
```

#### 5) Migraciones

```bash
python manage.py makemigrations notificaciones
python manage.py migrate
```

#### 6) (Opcional) Crear superusuario para entrar al admin

```bash
python manage.py createsuperuser
```

#### 7) Levantar el servidor

```bash
python manage.py runserver 0.0.0.0:8006
```

---

## URLs disponibles

| URL | Descripcion |
|---|---|
| `GET  /health/` | Health check |
| `GET  /admin/` | Admin de Django (requiere superusuario) |
| `GET  /api/docs/` | Swagger UI con todos los endpoints |
| `POST /notificaciones/bienvenida` | Email de bienvenida + clave unica |
| `POST /notificaciones/baja` | Avisa al docente de una baja |
| `POST /notificaciones/cierre-materia` | Envio masivo a alumnos |
| `POST /notificaciones/reset-password` | Link de reset de password |
| `GET  /notificaciones/` | Lista (filtrable por `?tipo=`, `?estado=`, `?email=`) |
| `GET  /notificaciones/<uuid>/` | Detalle |

---

## Probar con Postman

1. Abre Postman.
2. **Import** -> selecciona `postman/ms-notificaciones.postman_collection.json`.
3. La variable `baseUrl` ya viene en `http://localhost:8006`.
4. Ejecuta los requests en orden:
   - `Health Check`
   - `1. Enviar Bienvenida` (guarda el `id` automaticamente en `notificacionId`)
   - `2. Notificar Baja al Docente`
   - `3. Cierre de Materia`
   - `4. Reset de Contrasena`
   - `5. Listar Notificaciones`
   - `6. Ver detalle por ID` (usa el id guardado)

> En modo dev, `EMAIL_BACKEND=console`: los correos se imprimen en la terminal donde corre Django, no se envian de verdad.

### Probar con cURL

```bash
# Bienvenida
curl -X POST http://localhost:8006/notificaciones/bienvenida \
  -H "Content-Type: application/json" \
  -d '{
    "alumno_email": "juan@buap.mx",
    "alumno_nombre": "Juan Perez",
    "materia_nombre": "Servicios Web",
    "clave_unica": "ABC123"
  }'

# Listar
curl http://localhost:8006/notificaciones/
```

---

## Enviar correos REALES (Gmail)

Edita tu `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-correo@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password    # OJO: app password, NO la del Gmail
DEFAULT_FROM_EMAIL=AGM <tu-correo@gmail.com>
```

> Para crear un *App Password* en Gmail necesitas tener 2FA activo y crearlo en `myaccount.google.com/apppasswords`.

Reinicia el server. Los correos ahora se enviaran de verdad.

---

## Cuando integres gRPC con los demas microservicios

1. Copia los `.proto` desde `proto/` (raiz del repo) a este MS.
2. Corre `bash scripts/generate_protos.sh` para generar los stubs.
3. Descomenta el codigo en `grpc_server/services.py` y `grpc_server/server.py`.
4. En `apps/notificaciones/services.py`, cambia los placeholders por llamadas gRPC reales (ej: `MS-3 GetAlumnoById` para resolver email/nombre solo con el `alumno_id`).
5. Pon `STANDALONE_MODE=False` en `.env` y ajusta los `serializers.py` para volverlos a recibir solo IDs.

---

## Troubleshooting

| Sintoma | Solucion |
|---|---|
| `psycopg2.OperationalError: could not connect` | Postgres no esta corriendo. Verifica `DB_HOST` en `.env`. |
| `ModuleNotFoundError: dotenv` | `pip install -r requirements.txt` |
| Migraciones no se aplican | Borra `apps/notificaciones/migrations/0001_*.py` y vuelve a correr `makemigrations` |
| El correo no se ve en consola | Revisa que `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` |
| 403 / CSRF en POST | Ya esta configurado para aceptar JSON. Si persiste, revisa que mandas `Content-Type: application/json` |
