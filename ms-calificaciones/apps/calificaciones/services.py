import pandas as pd
from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.db.models import Avg
from .models import Calificacion, Actividad
from apps.ponderaciones.models import Ponderacion
from .alumnos_client import AlumnosClient

# NOTA: Aquí importarías tu cliente gRPC generado para cumplir con el aislamiento de datos
# from .client import AlumnosClient 

class CalificacionesService:
    @staticmethod
    def procesar_archivo_masivo(actividad_id, archivo):
        """
        Procesa archivos Excel o CSV para registrar calificaciones de forma masiva.
        Implementa un patrón de 'Upsert' (actualiza si existe, crea si no).
        """
        try:
            # Lectura del archivo según su extensión [cite: 39, 141]
            if archivo.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(archivo)
            else:
                df = pd.read_csv(archivo)
            
            # Atomicidad para garantizar la integridad de los datos en el MS-4 
            with transaction.atomic():
                for _, row in df.iterrows():
                    # El mapeo espera columnas 'alumno_id' y 'valor' en el archivo 
                    Calificacion.objects.update_or_create(
                        actividad_id=actividad_id,
                        alumno_id=str(row['alumno_id']),
                        defaults={'valor': Decimal(str(row['valor']))}
                    )
            return True, len(df)
        except Exception as e:
            return False, str(e)

    @staticmethod
    def obtener_concentrado_detallado(materia_id):
        """
        Genera el concentrado inyectando nombres reales desde MS-3 vía gRPC.
        """
        ponderaciones = Ponderacion.objects.filter(materia_id=materia_id)
        if not ponderaciones:
            return []

        alumnos_ids = Calificacion.objects.filter(
            actividad__ponderacion__materia_id=materia_id
        ).values_list('alumno_id', flat=True).distinct()

        # Instanciamos nuestro cliente actualizado
        client_ms3 = AlumnosClient()
        lista_final = []

        for alu_id in alumnos_ids:
            # Obtenemos los datos reales del contrato AlumnoInfo
            datos_alumno = client_ms3.obtener_datos_alumno(alu_id)
            
            promedio_final = Decimal('0.00')
            entregas = {}

            for pond in ponderaciones:
                califs_cat = Calificacion.objects.filter(alumno_id=alu_id, actividad__ponderacion=pond)
                
                if califs_cat.exists():
                    prom_cat = califs_cat.aggregate(Avg('valor'))['valor__avg'] or Decimal('0.00')
                    # Σ (promedio_categoria * porcentaje / 100)
                    promedio_final += (prom_cat * pond.porcentaje) / Decimal('100')
                    
                    for c in califs_cat:
                        entregas[c.actividad.nombre] = c.valor

            # Redondeo Institucional (>= 0.5 sube)
            promedio_redondeado = int(promedio_final.quantize(Decimal('1'), rounding=ROUND_HALF_UP))
            
            # Clasificación de Estatus
            estatus = "REPROBADO"
            if promedio_redondeado >= 8:
                estatus = "APROBADO"
            elif 6 <= promedio_redondeado < 8:
                estatus = "EN RIESGO"

            lista_final.append({
                "alumno_id": alu_id,
                "nombre_alumno": datos_alumno["nombre"],
                "matricula": datos_alumno["matricula"],
                "promedio_real": promedio_final,
                "promedio_redondeado": promedio_redondeado,
                "estatus": estatus,
                "entregas": entregas
            })

        return lista_final