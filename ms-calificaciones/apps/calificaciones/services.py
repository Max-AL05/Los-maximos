"""
Capa de servicios de calificaciones.

Encapsula:
    - Importación masiva de calificaciones desde Excel/CSV.
    - Cálculo del concentrado de una materia (promedios y estatus).

El concentrado obtiene la lista oficial de inscritos vía gRPC (MS-3),
no a partir de quién tenga calificaciones cargadas. Esto cubre dos casos
que el código previo se perdía:
    a) alumnos inscritos que aún no han recibido ninguna nota
       → aparecen con promedio 0.00 y estatus REPROBADO (correcto).
    b) alumnos con notas pero ya dados de baja
       → se filtran con `activo_en_materia` y NO aparecen.
"""
import logging
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

import pandas as pd
from django.db import transaction
from django.db.models import Avg

from apps.ponderaciones.models import Ponderacion

from .alumnos_client import AlumnosClient
from .models import Calificacion


logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Constantes de negocio – centralizadas para que los serializers, el grpc_server
# y este módulo coincidan en los mismos umbrales y los mismos strings.
# ─────────────────────────────────────────────────────────────────────────────
ESTATUS_APROBADO  = "APROBADO"
ESTATUS_EN_RIESGO = "EN_RIESGO"     # underscore: coincide con el .proto
ESTATUS_REPROBADO = "REPROBADO"


def calcular_estatus(promedio_redondeado: int) -> str:
    """
    OJO – Decisión de negocio:
        >= 8     → APROBADO
        6 ó 7    → EN_RIESGO
        <= 5     → REPROBADO

    El umbral institucional típico es 6 = APROBADO. Si tu equipo decidió que
    EN_RIESGO existe para alumnos en 6/7, mantén estos umbrales pero
    confírmalos con quien hace MS-7 Reportes; si MS-7 considera 6 como
    aprobado y tú como en-riesgo, los reportes y el concentrado discreparán
    para el mismo alumno.
    """
    if promedio_redondeado >= 8:
        return ESTATUS_APROBADO
    if promedio_redondeado >= 6:
        return ESTATUS_EN_RIESGO
    return ESTATUS_REPROBADO


def redondeo_institucional(valor: Decimal) -> int:
    """>= 0.5 sube al entero superior; < 0.5 baja."""
    return int(valor.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


# ─────────────────────────────────────────────────────────────────────────────
# Servicio
# ─────────────────────────────────────────────────────────────────────────────
class CalificacionesService:

    # ───────────── Importación masiva ─────────────
    @staticmethod
    def procesar_archivo_masivo(actividad_id, archivo) -> tuple[bool, int | str]:
        """
        Patrón upsert: actualiza si existe, crea si no.
        Atómico: si una fila truena, ninguna se persiste.

        Espera columnas `alumno_id` y `valor` en el archivo.
        """
        try:
            if archivo.name.lower().endswith((".xlsx", ".xls")):
                df = pd.read_excel(archivo)
            elif archivo.name.lower().endswith(".csv"):
                df = pd.read_csv(archivo)
            else:
                return False, "Formato no soportado. Usa .xlsx, .xls o .csv."

            requeridas = {"alumno_id", "valor"}
            if not requeridas.issubset(df.columns):
                faltan = requeridas - set(df.columns)
                return False, f"El archivo no tiene la(s) columna(s): {', '.join(faltan)}."

            with transaction.atomic():
                for _, row in df.iterrows():
                    Calificacion.objects.update_or_create(
                        actividad_id=actividad_id,
                        alumno_id=str(row["alumno_id"]).strip(),
                        defaults={"valor": Decimal(str(row["valor"]))},
                    )
            return True, len(df)

        except (ValueError, InvalidOperation) as e:
            return False, f"Datos inválidos: {e}"
        except Exception as e:
            logger.exception("Error en importación masiva")
            return False, str(e)

    # ───────────── Concentrado ─────────────
    @staticmethod
    def obtener_concentrado_detallado(materia_id: str) -> list[dict]:
        """
        Devuelve la lista de alumnos inscritos con sus promedios ponderados.

        Pasos:
            1. Validar que existe rúbrica (Ponderaciones) para la materia.
            2. Una sola RPC a MS-3 → lista de inscritos activos.
            3. Para cada uno: aplicar Σ (avg(categoría) * porcentaje / 100).
            4. Redondeo institucional + estatus.

        Si MS-3 está caído, regresa lista vacía y deja que el caller
        decida qué responder al cliente (ver views.py).
        """
        ponderaciones = list(Ponderacion.objects.filter(materia_id=materia_id))
        if not ponderaciones:
            return []

        # 1 sola llamada gRPC para todos los inscritos activos.
        client_ms3 = AlumnosClient()
        alumnos = client_ms3.obtener_alumnos_de_materia(materia_id, solo_activos=True)
        if not alumnos:
            # Puede ser que la materia exista pero no tenga inscritos,
            # o bien que MS-3 no respondió. El caller diferencia con
            # logs; aquí solo regresamos vacío.
            logger.info(
                "obtener_concentrado_detallado: MS-3 no devolvió inscritos para materia=%s",
                materia_id,
            )
            return []

        lista_final = []
        for alumno in alumnos:
            promedio_final = Decimal("0.00")
            entregas: dict[str, Decimal] = {}

            for pond in ponderaciones:
                califs_cat = Calificacion.objects.filter(
                    alumno_id=alumno["alumno_id"],
                    actividad__ponderacion=pond,
                )
                if not califs_cat.exists():
                    continue

                prom_cat = califs_cat.aggregate(Avg("valor"))["valor__avg"] or Decimal("0.00")
                promedio_final += (prom_cat * pond.porcentaje) / Decimal("100")

                for c in califs_cat.select_related("actividad"):
                    entregas[c.actividad.nombre] = c.valor

            redondeado = redondeo_institucional(promedio_final)
            lista_final.append({
                "alumno_id":           alumno["alumno_id"],
                "matricula":           alumno["matricula"],
                "nombre_completo":     alumno["nombre_completo"],
                # Compat con tu serializer actual (espera `nombre_alumno`):
                "nombre_alumno":       alumno["nombre_completo"],
                "promedio_real":       promedio_final,
                "promedio_redondeado": redondeado,
                "estatus":             calcular_estatus(redondeado),
                "entregas":            entregas,
            })

        return lista_final