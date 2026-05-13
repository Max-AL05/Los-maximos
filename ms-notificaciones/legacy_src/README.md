# Legacy Source — Código Fuente Heredado

## 1. Propósito de este Directorio

El directorio `/legacy_src` contiene la totalidad del código fuente del sistema web **Patitas Home** en su versión original, desarrollada de forma manual sin el empleo de técnicas de Ingeniería Basada en Modelos. Este código constituye la **línea base** (baseline) a partir de la cual se ha diseñado el proceso de migración hacia una arquitectura generada automáticamente.

> **Advertencia:** Este directorio tiene un carácter exclusivamente referencial. El código aquí contenido **no forma parte** del flujo de generación automática y será **deprecado progresivamente** a medida que la fábrica de software alcance la paridad funcional con el sistema original.

---

## 2. Estructura Interna

| Subdirectorio | Tecnología | Descripción |
|---|---|---|
| `/frontend_angular` | Angular (TypeScript, HTML, CSS) | Aplicación de interfaz de usuario desarrollada manualmente con el framework Angular. Incluye componentes, servicios, módulos de enrutamiento y archivos de configuración propios del ecosistema Angular CLI. |
| `/backend_django` | Django (Python) | Aplicación de servidor desarrollada manualmente con el framework Django. Incluye modelos ORM, vistas, serializadores (Django REST Framework), configuraciones de URL y archivos de migración de base de datos. |

---

## 3. Rol dentro del Proyecto

El código heredado cumple las siguientes funciones dentro del contexto del proyecto:

1. **Referencia Funcional:** Permite identificar los requisitos funcionales implementados en el sistema original y verificar que la aplicación generada automáticamente los replique de forma equivalente.
2. **Análisis de Dominio:** Sirve como insumo para la extracción de entidades, relaciones y reglas de negocio que alimentan la construcción de los modelos CIM y PIM en el directorio `/modelado_uml`.
3. **Validación Comparativa:** Facilita la comparación directa entre el código escrito manualmente y el código producido por las plantillas EGL, permitiendo evaluar la calidad y completitud de la generación automática.
4. **Trazabilidad Histórica:** Documenta el estado inicial del sistema antes de la intervención del pipeline de transformación basado en modelos.

---

## 4. Política de Deprecación

El código contenido en este directorio seguirá el siguiente ciclo de deprecación:

| Fase | Estado | Descripción |
|---|---|---|
| Fase 1 | **Activa** | El código heredado se mantiene como referencia activa durante el diseño de los metamodelos y las transformaciones. |
| Fase 2 | En deprecación | Una vez que la fábrica de software genere código funcionalmente equivalente, el código heredado se marcará como obsoleto. |
| Fase 3 | Archivado | El código heredado se moverá a una rama de archivo (`archive/legacy`) o se eliminará del repositorio principal. |

---

## 5. Restricciones de Uso

- **No se debe ejecutar** el código heredado como sistema de producción en paralelo con la aplicación generada.
- **No se deben realizar modificaciones** al código heredado salvo que sea estrictamente necesario para fines de documentación o análisis comparativo.
- **No se debe copiar** código de este directorio hacia `/app_generada`. Todo el código en la aplicación generada debe provenir exclusivamente del pipeline de transformación (ETL + EGL).

---

## 6. Dependencias del Código Heredado

### 6.1 Frontend Angular

- Node.js y npm (versión compatible con el proyecto Angular original).
- Angular CLI.
- Dependencias especificadas en el archivo `package.json` correspondiente.

### 6.2 Backend Django

- Python 3.x.
- Django y Django REST Framework.
- Dependencias especificadas en el archivo `requirements.txt` correspondiente.
- Base de datos compatible (PostgreSQL, SQLite u otra según la configuración original).

> **Nota:** La instalación y ejecución de estas dependencias es opcional y solo se requiere si se desea levantar el sistema heredado con fines de comparación o análisis.
