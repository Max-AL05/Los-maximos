# AGM – Sistema de Gestión y Automatización de Calificaciones

Backend con arquitectura de **microservicios** para la Facultad de Ciencias de la Computación – BUAP.
Comunicación interna **gRPC** + comunicación externa **REST/HTTP**.

> Proyecto Final – Servicios Web

## 🧩 Microservicios

| MS | Nombre | Puerto REST | Puerto gRPC | BD |
|----|--------|-------------|-------------|----|
| MS-1 | Auth & Users | 8001 | 50051 | PostgreSQL (`agm_auth_db`) |
| MS-2 | Periodos & Materias | 8002 | 50052 | PostgreSQL (`agm_periodos_db`) |
| MS-3 | Docentes & Alumnos | 8003 | 50053 | PostgreSQL (`agm_alumnos_db`) |
| MS-4 | Calificaciones & Ponderaciones | 8004 | 50054 | PostgreSQL (`agm_calif_db`) |
| MS-5 | Asistencias QR | 8005 | 50055 | PostgreSQL + Redis |
| MS-6 | Notificaciones | 8006 | 50056 | PostgreSQL (`agm_notif_db`) |
| MS-7 | Reportes & Estadísticas | 8007 | 50057 | PostgreSQL (`agm_reportes_db`) |

## 📁 Estructura

```
agm-backend/
├── docker-compose.yml          # Orquestación local de todo el sistema
├── proto/                      # Contratos gRPC (.proto compartidos)
│   ├── auth.proto
│   ├── periodos.proto
│   ├── alumnos.proto
│   ├── calificaciones.proto
│   ├── asistencias.proto
│   ├── notificaciones.proto
│   └── reportes.proto
├── ms-auth/                    # MS-1 Django + DRF
├── ms-periodos/                # MS-2 Django + DRF
├── ms-alumnos/                 # MS-3 Django + DRF
├── ms-calificaciones/          # MS-4 Django + DRF
├── ms-asistencias/             # MS-5 Django + DRF + Redis
├── ms-notificaciones/          # MS-6 Django + DRF
├── ms-reportes/                # MS-7 Django + DRF
└── scripts/
    └── generate_protos.sh      # Genera código gRPC en cada MS
```

## 🚀 Levantar el sistema localmente

```bash
# 1. Clonar
git clone <repo>
cd agm-backend

# 2. Configurar variables de entorno (copiar .env.example en cada MS)
for d in ms-*/; do cp $d.env.example $d.env; done

# 3. Generar código gRPC a partir de los .proto
bash scripts/generate_protos.sh

# 4. Levantar todo
docker-compose up --build
```

## 👥 Equipo


## 📺 Demo

URL del video: _por completar_

## 🌐 URLs de producción

_por completar al desplegar_
