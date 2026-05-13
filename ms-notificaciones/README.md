# Patitas Home — Fábrica de Software Basada en Modelos

## 1. Descripción General del Proyecto

**Patitas Home** es un proyecto académico cuyo objetivo central es demostrar la viabilidad de migrar un sistema web heredado —desarrollado manualmente con **Angular** (frontend) y **Django** (backend)— hacia una arquitectura completamente generada de forma automática mediante técnicas de **Ingeniería Basada en Modelos (Model-Based Development, MBD)**.

El proyecto implementa una **fábrica de software** (software factory) que, a partir de modelos conceptuales expresados en **PlantUML**, metamodelos definidos con **Eclipse Modeling Framework (EMF)** y reglas de transformación/generación escritas en el lenguaje **Epsilon**, produce código ejecutable sin intervención manual en la capa de implementación.

---

## 2. Justificación Técnica

La motivación principal de este proyecto reside en la necesidad de:

1. **Reducir el acoplamiento** entre la lógica de negocio y la plataforma tecnológica concreta.
2. **Garantizar la trazabilidad** entre los requisitos del dominio y el código fuente generado.
3. **Automatizar la generación de artefactos** de software (código fuente, configuraciones, esquemas de base de datos) a partir de especificaciones abstractas.
4. **Demostrar la aplicabilidad** del enfoque MDA (Model-Driven Architecture) de la OMG en un contexto académico controlado.

---

## 3. Estructura del Repositorio

La organización del repositorio refleja la separación de responsabilidades propia de una arquitectura dirigida por modelos. A continuación se describe cada directorio de primer nivel:

| Directorio | Propósito | Contenido Principal |
|---|---|---|
| [`/legacy_src`](./legacy_src) | Código fuente heredado (referencia) | Proyecto Angular original y proyecto Django original |
| [`/modelado_uml`](./modelado_uml) | Modelos conceptuales del dominio | Diagramas PlantUML organizados en niveles CIM y PIM |
| [`/arquitectura_mbd`](./arquitectura_mbd) | Núcleo de la fábrica de software | Metamodelos `.ecore` (EMF), scripts `.etl` (ETL) y plantillas `.egl` (EGL) |
| [`/app_generada`](./app_generada) | Código generado automáticamente | Frontend (TypeScript/HTML) y Backend (Python) producidos por EGL |
| `docker-compose.yml` | Orquestación de contenedores | Definición de servicios para despliegue local |
| `.gitignore` | Control de versiones | Exclusiones de archivos temporales y generados |

---

## 4. Flujo de Transformación (Pipeline MBD)

El proceso de generación automática de código sigue un flujo unidireccional que puede resumirse en las siguientes etapas:

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Diagramas UML  │     │   Metamodelos    │     │  Transformación  │     │ Código Generado  │
│   (PlantUML)     │────▶│   (.ecore / EMF) │────▶│  (.etl) + (.egl) │────▶│  (app_generada)  │
│   CIM ──▶ PIM    │     │   Reglas         │     │  Epsilon         │     │  Frontend + Back │
└──────────────────┘     └──────────────────┘     └──────────────────┘     └──────────────────┘
    /modelado_uml           /arquitectura_mbd        /arquitectura_mbd        /app_generada
                              /metamodelos             /transformaciones
```

1. **Modelado Conceptual (CIM/PIM):** Se definen los diagramas de dominio y de plataforma independiente en PlantUML.
2. **Definición de Metamodelos:** Se formalizan las reglas estructurales del dominio mediante archivos `.ecore` en EMF.
3. **Transformación y Generación:** Los scripts ETL transforman los modelos, y las plantillas EGL generan el código fuente final.
4. **Salida (Output):** El código generado se deposita en `/app_generada`, listo para su compilación y despliegue.

---

## 5. Stack Tecnológico

| Capa | Tecnología | Versión / Especificación |
|---|---|---|
| Modelado Visual | PlantUML | Última versión estable |
| Metamodelado | Eclipse Modeling Framework (EMF) | `.ecore` / Ecore |
| Transformación Modelo-a-Modelo | Epsilon Transformation Language (ETL) | Epsilon 2.x |
| Generación Modelo-a-Texto | Epsilon Generation Language (EGL) | Epsilon 2.x |
| Frontend Heredado | Angular | Según versión original |
| Backend Heredado | Django (Python) | Según versión original |
| Frontend Generado | TypeScript / HTML | Generado por EGL |
| Backend Generado | Python | Generado por EGL |
| Contenedores | Docker / Docker Compose | Última versión estable |

---

## 6. Relación con el Código Heredado

El directorio `/legacy_src` contiene el código fuente del sistema original desarrollado manualmente. Este código cumple exclusivamente una función de **referencia temporal**: permite contrastar la implementación manual con la generada automáticamente. A medida que la fábrica de software alcance la paridad funcional, el código heredado será **deprecado progresivamente** hasta su eventual eliminación del repositorio.

> **Nota:** Bajo ninguna circunstancia debe mezclarse código escrito manualmente con el código producido por la fábrica de software en el directorio `/app_generada`.

---

## 7. Instrucciones de Uso

### 7.1 Prerrequisitos

- Eclipse IDE con los plugins de EMF y Epsilon instalados.
- PlantUML (integrado en Eclipse o como herramienta independiente).
- Docker y Docker Compose para el despliegue de la aplicación generada.
- Java Runtime Environment (JRE) 11 o superior para la ejecución de Epsilon.

### 7.2 Ejecución del Pipeline de Generación

1. Abrir el proyecto en Eclipse IDE.
2. Verificar que los metamodelos en `/arquitectura_mbd/metamodelos` estén correctamente registrados en el registro de paquetes EMF.
3. Ejecutar los scripts ETL ubicados en `/arquitectura_mbd/transformaciones` para aplicar las transformaciones modelo-a-modelo.
4. Ejecutar las plantillas EGL ubicadas en `/arquitectura_mbd/transformaciones` para generar el código fuente en `/app_generada`.
5. Desplegar la aplicación generada utilizando Docker Compose:

```bash
docker-compose up --build
```