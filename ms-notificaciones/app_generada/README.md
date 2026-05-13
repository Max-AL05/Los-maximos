# Aplicación Generada — Código Producido Automáticamente

## 1. Propósito de este Directorio

El directorio `/app_generada` constituye el **destino final (output)** del pipeline de generación automática de código del proyecto Patitas Home. Todo el contenido de este directorio es producido exclusivamente por las plantillas **EGL (Epsilon Generation Language)** a partir de los metamodelos Ecore y las transformaciones ETL definidos en `/arquitectura_mbd`.

> **ADVERTENCIA CRÍTICA:** Ningún archivo dentro de este directorio debe ser creado, modificado o eliminado de forma manual. Cualquier intervención manual será sobrescrita en la siguiente ejecución del pipeline de generación y comprometerá la integridad del enfoque basado en modelos.

---

## 2. Estructura Interna

| Subdirectorio | Tecnología de Salida | Descripción |
|---|---|---|
| `/frontend` | TypeScript, HTML, CSS | Código fuente de la aplicación de interfaz de usuario, generado a partir de las plantillas EGL correspondientes al frontend. |
| `/backend` | Python | Código fuente de la aplicación de servidor, generado a partir de las plantillas EGL correspondientes al backend. |

---

## 3. Contenido del Subdirectorio `/frontend`

El subdirectorio `/frontend` contiene el código de la capa de presentación del sistema, generado en **TypeScript** y **HTML**. Los artefactos típicos producidos incluyen:

| Tipo de Artefacto | Descripción |
|---|---|
| Componentes | Archivos TypeScript y HTML que definen los componentes de la interfaz de usuario. |
| Servicios | Clases TypeScript que encapsulan la comunicación con el backend (llamadas HTTP). |
| Modelos/Interfaces | Definiciones de tipos TypeScript que reflejan las entidades del dominio. |
| Módulos de Enrutamiento | Configuraciones de navegación generadas a partir del modelo de casos de uso. |
| Archivos de Configuración | Archivos de configuración del proyecto frontend (package.json, tsconfig.json, etc.). |

---

## 4. Contenido del Subdirectorio `/backend`

El subdirectorio `/backend` contiene el código de la capa de servidor del sistema, generado en **Python**. Los artefactos típicos producidos incluyen:

| Tipo de Artefacto | Descripción |
|---|---|
| Modelos de Datos | Clases Python que definen las entidades del dominio y su mapeo a la base de datos (ORM). |
| Vistas / Endpoints | Definiciones de endpoints de la API REST generados a partir de las operaciones del modelo. |
| Serializadores | Clases que gestionan la conversión entre objetos Python y representaciones JSON. |
| Configuración de URLs | Archivos de enrutamiento que mapean las rutas HTTP a las vistas correspondientes. |
| Migraciones | Scripts de migración de base de datos derivados de los modelos de datos generados. |
| Archivos de Configuración | Archivos de configuración del proyecto backend (settings, requirements.txt, etc.). |

---

## 5. Política de No Modificación Manual

### 5.1 Fundamento

La integridad del enfoque de Ingeniería Basada en Modelos depende de que el código generado sea un reflejo fiel y exclusivo de los modelos y las transformaciones definidas en el pipeline. La modificación manual del código generado introduce las siguientes problemáticas:

1. **Pérdida de Trazabilidad:** Se rompe la cadena de trazabilidad entre los modelos conceptuales y el código ejecutable.
2. **Sobrescritura:** Las modificaciones manuales serán eliminadas en la siguiente ejecución del pipeline de generación.
3. **Inconsistencia:** El código modificado manualmente puede divergir de las especificaciones del metamodelo, generando comportamientos no previstos.
4. **Invalidación de la Verificación:** La validación automática del código generado contra los modelos pierde su validez si el código ha sido alterado.

### 5.2 Protocolo de Cambios

Si se detecta un defecto o una carencia en el código generado, el procedimiento correcto es:

1. Identificar la plantilla EGL o el metamodelo Ecore responsable del artefacto defectuoso.
2. Corregir la plantilla o el metamodelo en `/arquitectura_mbd`.
3. Re-ejecutar el pipeline de generación completo.
4. Verificar que el código regenerado en `/app_generada` refleje la corrección.

> **Bajo ninguna circunstancia** se debe aplicar un parche directo sobre los archivos de este directorio.

---

## 6. Regeneración del Código

Para regenerar el contenido completo de este directorio, se deben seguir los siguientes pasos:

1. Abrir el proyecto en Eclipse IDE con los plugins de EMF y Epsilon.
2. Verificar que los metamodelos en `/arquitectura_mbd/metamodelos` estén registrados.
3. Ejecutar el script de coordinación `.egx` en `/arquitectura_mbd/transformaciones`.
4. El código generado se depositará automáticamente en los subdirectorios `/frontend` y `/backend`.

---

## 7. Despliegue

Una vez generado el código, la aplicación puede desplegarse mediante Docker Compose desde la raíz del proyecto:

```bash
docker-compose up --build
```

El archivo `docker-compose.yml` de la raíz del proyecto está configurado para construir y orquestar los servicios del frontend y el backend a partir del código contenido en este directorio.

---

## 8. Control de Versiones

### 8.1 Inclusión en Git

Se recomienda incluir el código generado en el repositorio Git para los siguientes fines:

- Permitir la revisión del código generado sin necesidad de ejecutar el pipeline.
- Facilitar la comparación entre versiones sucesivas del código generado.
- Garantizar la reproducibilidad del despliegue en entornos donde no se disponga de Eclipse y Epsilon.

### 8.2 Alternativa: Exclusión de Git

En caso de que el equipo opte por excluir el código generado del repositorio (tratándolo como un artefacto derivado), se debe añadir la siguiente entrada al archivo `.gitignore` de la raíz:

```gitignore
/app_generada/frontend/
/app_generada/backend/
```

En este escenario, la regeneración del código será un paso obligatorio previo al despliegue.
