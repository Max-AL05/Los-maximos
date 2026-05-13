# Arquitectura MBD — Núcleo de la Fábrica de Software

## 1. Propósito de este Directorio

El directorio `/arquitectura_mbd` contiene el **núcleo operativo** de la fábrica de software del proyecto Patitas Home. Aquí residen los artefactos que definen las reglas de estructura del dominio (metamodelos), las transformaciones modelo-a-modelo y las plantillas de generación de código modelo-a-texto.

Este directorio implementa las capas centrales del enfoque **Model-Driven Architecture (MDA)**: la formalización de los modelos conceptuales en metamodelos ejecutables y la automatización de la producción de código fuente a partir de dichos metamodelos.

---

## 2. Estructura Interna

| Subdirectorio | Contenido | Tecnología |
|---|---|---|
| `/metamodelos` | Definiciones estructurales del dominio en formato Ecore | Eclipse Modeling Framework (EMF) |
| `/transformaciones` | Scripts de transformación y plantillas de generación de código | Epsilon (ETL + EGL) |

---

## 3. Subdirectorio `/metamodelos` — Definiciones Ecore (EMF)

### 3.1 Descripción

El subdirectorio `/metamodelos` almacena los archivos **`.ecore`** que definen los metamodelos del sistema. Un metamodelo Ecore especifica de forma formal y ejecutable la estructura del dominio: las clases, los atributos, los tipos de datos, las relaciones (referencias, composiciones, herencias) y las restricciones que deben satisfacer las instancias del modelo.

Los metamodelos Ecore constituyen el **contrato estructural** entre los modelos conceptuales (definidos en `/modelado_uml`) y el código generado (depositado en `/app_generada`).

### 3.2 Archivos Esperados

| Extensión | Descripción |
|---|---|
| `.ecore` | Definición del metamodelo en formato XML/XMI conforme al estándar Ecore de EMF. |
| `.genmodel` | Modelo de generación asociado que parametriza la producción de código Java a partir del `.ecore` (opcional, según el flujo del proyecto). |
| `.ecorediag` | Diagrama visual del metamodelo generado por el editor gráfico de EMF (opcional). |

### 3.3 Principios de Diseño

1. **Fidelidad al PIM:** Cada clase y relación del metamodelo debe tener una correspondencia directa con los elementos definidos en los diagramas PIM de `/modelado_uml/pim`.
2. **Minimalismo:** El metamodelo debe contener exclusivamente los elementos necesarios para la generación de código. Se debe evitar la inclusión de elementos decorativos o redundantes.
3. **Restricciones OCL:** Cuando sea necesario, las invariantes y restricciones del dominio deben expresarse mediante anotaciones OCL (Object Constraint Language) integradas en el metamodelo.
4. **Modularidad:** Para sistemas de complejidad significativa, se recomienda descomponer el dominio en múltiples archivos `.ecore` interrelacionados.

---

## 4. Subdirectorio `/transformaciones` — Scripts ETL y Plantillas EGL

### 4.1 Descripción

El subdirectorio `/transformaciones` contiene los artefactos ejecutables del motor de generación, implementados con el framework **Epsilon**:

- **Scripts ETL (Epsilon Transformation Language):** Definen las reglas de transformación modelo-a-modelo (M2M). Permiten transformar instancias de un metamodelo fuente en instancias de un metamodelo destino, aplicando lógica de mapeo, filtrado y enriquecimiento.
- **Plantillas EGL (Epsilon Generation Language):** Definen las reglas de generación modelo-a-texto (M2T). Cada plantilla consume un modelo conforme a un metamodelo Ecore y produce archivos de texto (código fuente, configuraciones, esquemas) como salida.

### 4.2 Archivos Esperados

| Extensión | Tipo | Descripción |
|---|---|---|
| `.etl` | Transformación M2M | Script que define reglas de transformación entre modelos. Cada regla especifica una correspondencia entre elementos del modelo fuente y elementos del modelo destino. |
| `.egl` | Generación M2T | Plantilla que define la estructura del código fuente a generar. Combina texto estático con expresiones dinámicas que extraen información del modelo de entrada. |
| `.egx` | Coordinación EGL | Script de coordinación que orquesta la ejecución de múltiples plantillas EGL, asignando a cada una el modelo de entrada y la ruta de salida correspondiente. |
| `.eol` | Lógica auxiliar | Script en Epsilon Object Language que define operaciones auxiliares reutilizables por los scripts ETL y las plantillas EGL. |

### 4.3 Flujo de Ejecución

El orden de ejecución de los artefactos de transformación es el siguiente:

1. **Carga del metamodelo:** Se registra el archivo `.ecore` en el registro de paquetes EMF.
2. **Carga del modelo fuente:** Se carga la instancia del modelo conforme al metamodelo registrado.
3. **Transformación ETL (opcional):** Si se requiere una transformación intermedia, se ejecuta el script `.etl` correspondiente.
4. **Generación EGL:** Se ejecuta el script de coordinación `.egx`, el cual invoca las plantillas `.egl` para cada elemento del modelo y produce los archivos de salida en `/app_generada`.

### 4.4 Convenciones de Nomenclatura

```
<capa>_<tipo_artefacto>_<nombre_descriptivo>.<extensión>
```

**Ejemplos:**
- `frontend_generador_componentes.egl`
- `backend_generador_modelos.egl`
- `pim_a_psm_transformacion.etl`
- `coordinador_frontend.egx`

---

## 5. Relación entre Metamodelos y Transformaciones

```
/metamodelos                        /transformaciones
┌────────────────────┐             ┌────────────────────┐
│  dominio.ecore     │────────────▶│  transformar.etl   │
│  (Metamodelo EMF)  │             │  (Reglas M2M)      │
│                    │             ├────────────────────┤
│  Clases            │             │  generar.egx       │
│  Atributos         │────────────▶│  (Coordinador)     │
│  Relaciones        │             ├────────────────────┤
│  Restricciones     │             │  plantilla.egl     │
│                    │             │  (Generación M2T)  │
└────────────────────┘             └─────────┬──────────┘
                                             │
                                             ▼
                                   /app_generada
                                   ┌────────────────────┐
                                   │  Código TypeScript  │
                                   │  Código Python      │
                                   │  Configuraciones    │
                                   └────────────────────┘
```

---

## 6. Herramientas Requeridas

| Herramienta | Versión Recomendada | Propósito |
|---|---|---|
| Eclipse IDE | 2023-09 o superior | Entorno de desarrollo con soporte para EMF y Epsilon |
| Eclipse Modeling Framework (EMF) | Integrado en Eclipse Modeling Tools | Creación y gestión de metamodelos Ecore |
| Epsilon Framework | 2.x | Ejecución de scripts ETL, plantillas EGL y scripts de coordinación EGX |
| Java Runtime Environment (JRE) | 11 o superior | Entorno de ejecución para Eclipse y Epsilon |

---

## 7. Directrices de Mantenimiento

1. **Sincronización:** Todo cambio en el metamodelo (`.ecore`) debe verificarse contra las transformaciones y plantillas existentes para evitar inconsistencias.
2. **Pruebas de Generación:** Después de cada modificación, se debe ejecutar el pipeline completo y verificar que el código generado en `/app_generada` sea correcto y compilable.
3. **Documentación Interna:** Cada script ETL y cada plantilla EGL deben incluir comentarios que describan su propósito, las entradas esperadas y las salidas producidas.
4. **Control de Versiones:** Los archivos de este directorio son artefactos críticos del proyecto y deben someterse a revisión de código antes de su integración en la rama principal.
