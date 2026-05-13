# Modelado UML — Diagramas Conceptuales del Dominio

## 1. Propósito de este Directorio

El directorio `/modelado_uml` constituye el **repositorio central de modelos conceptuales** del proyecto Patitas Home. Almacena los diagramas elaborados en **PlantUML** que describen el dominio del sistema desde distintos niveles de abstracción, siguiendo la taxonomía propuesta por la arquitectura **MDA (Model-Driven Architecture)** de la OMG (Object Management Group).

Estos modelos representan el punto de entrada del pipeline de transformación y constituyen la **fuente de verdad** (single source of truth) a partir de la cual se derivan los metamodelos, las transformaciones y, en última instancia, el código generado.

---

## 2. Estructura Interna

| Subdirectorio | Nivel de Abstracción | Descripción |
|---|---|---|
| `/cim` | Modelo Independiente de la Computación (CIM) | Diagramas que describen el dominio del negocio sin referencia alguna a aspectos computacionales o tecnológicos. |
| `/pim` | Modelo Independiente de la Plataforma (PIM) | Diagramas que describen la estructura lógica del sistema sin vinculación a una plataforma tecnológica específica. |

---

## 3. Modelo Independiente de la Computación (CIM)

### 3.1 Definición

El **CIM** (Computation-Independent Model) representa la vista del sistema desde la perspectiva exclusiva del dominio de negocio. En este nivel de abstracción, no se consideran aspectos de implementación, tecnología ni arquitectura de software. El objetivo es capturar los conceptos, las reglas de negocio y los procesos del dominio de forma pura.

### 3.2 Tipos de Diagramas Esperados

| Tipo de Diagrama | Propósito |
|---|---|
| Diagrama de Casos de Uso | Identificar los actores del sistema y las funcionalidades principales desde la perspectiva del usuario. |
| Diagrama de Actividades | Modelar los flujos de negocio y los procesos operativos del dominio. |
| Diagrama de Clases de Dominio | Representar las entidades del negocio y sus relaciones conceptuales sin considerar la persistencia ni la interfaz. |

### 3.3 Convenciones de Nomenclatura

Los archivos PlantUML dentro de `/cim` deben seguir la siguiente convención:

```
cim_<tipo_diagrama>_<nombre_descriptivo>.puml
```

**Ejemplos:**
- `cim_casos_uso_adopcion.puml`
- `cim_actividades_registro_mascota.puml`
- `cim_clases_dominio_principal.puml`

---

## 4. Modelo Independiente de la Plataforma (PIM)

### 4.1 Definición

El **PIM** (Platform-Independent Model) representa la vista del sistema en un nivel de abstracción que incluye decisiones de diseño de software, pero sin vinculación a una plataforma tecnológica concreta (por ejemplo, sin referencia a Angular, Django, PostgreSQL u otra tecnología específica).

El PIM actúa como **puente** entre la especificación del dominio (CIM) y la implementación concreta. Es el modelo que alimenta directamente a los metamodelos EMF y a las transformaciones ETL.

### 4.2 Tipos de Diagramas Esperados

| Tipo de Diagrama | Propósito |
|---|---|
| Diagrama de Clases de Diseño | Definir las clases, atributos, operaciones y relaciones que conforman la arquitectura lógica del sistema. |
| Diagrama de Secuencia | Modelar las interacciones entre objetos para los casos de uso más relevantes. |
| Diagrama de Componentes | Representar la organización modular del sistema en componentes lógicos. |
| Diagrama de Estados | Modelar el ciclo de vida de las entidades clave del dominio. |

### 4.3 Convenciones de Nomenclatura

Los archivos PlantUML dentro de `/pim` deben seguir la siguiente convención:

```
pim_<tipo_diagrama>_<nombre_descriptivo>.puml
```

**Ejemplos:**
- `pim_clases_diseno_sistema.puml`
- `pim_secuencia_proceso_adopcion.puml`
- `pim_componentes_arquitectura.puml`

---

## 5. Relación con el Pipeline de Transformación

Los modelos almacenados en este directorio participan en el flujo de transformación de la siguiente manera:

1. Los diagramas **CIM** informan las decisiones de modelado a nivel de dominio.
2. Los diagramas **PIM** se formalizan en metamodelos **Ecore** y sirven como entrada para las transformaciones **ETL**.
3. Las plantillas **EGL** consumen los modelos transformados y producen el código fuente depositado en `/app_generada`.

---

## 6. Herramientas Requeridas

| Herramienta | Uso | Integración |
|---|---|---|
| PlantUML | Renderizado de diagramas `.puml` | Plugin de Eclipse, extensión de VS Code o línea de comandos |
| Graphviz | Motor de renderizado gráfico (dependencia de PlantUML) | Instalación a nivel de sistema operativo |

---

## 7. Directrices de Mantenimiento

1. **Consistencia:** Todo cambio en los modelos CIM o PIM debe reflejarse en los metamodelos y transformaciones correspondientes dentro de `/arquitectura_mbd`.
2. **Versionamiento:** Los archivos `.puml` deben versionarse junto con el resto del repositorio. Se recomienda documentar los cambios significativos en los mensajes de commit.
3. **Validación:** Antes de ejecutar el pipeline de transformación, se debe verificar que los diagramas PlantUML compilen correctamente y que su contenido sea coherente con los metamodelos definidos.
4. **Granularidad:** Se prefiere un diagrama por concepto o proceso, evitando archivos monolíticos que dificulten la legibilidad y el mantenimiento.
