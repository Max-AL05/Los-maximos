import grpc
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Avg, Max, Min

# Importamos los modelos de las apps
from apps.calificaciones.models import Calificacion
from apps.ponderaciones.models import Ponderacion

# Importamos los archivos generados por protoc
# Asegúrate de que la carpeta 'protos' sea importable
import protos.calificaciones_pb2 as calificaciones_pb2
import protos.calificaciones_pb2_grpc as calificaciones_pb2_grpc

class CalificacionesServicer(calificaciones_pb2_grpc.CalificacionesServiceServicer):
    
    def GetConcentrado(self, request, context):
        """
        Implementa GetConcentrado: Σ (promedio_categoria * porcentaje / 100)
        Retorna el listado de alumnos con promedios y estatus.
        """
        materia_id = request.materia_id
        ponderaciones = Ponderacion.objects.filter(materia_id=materia_id)
        
        if not ponderaciones.exists():
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"No hay rúbrica configurada para la materia {materia_id}")
            return calificaciones_pb2.GetConcentradoResponse()

        # Obtenemos alumnos únicos con notas en esta materia
        alumnos_ids = Calificacion.objects.filter(
            actividad__ponderacion__materia_id=materia_id
        ).values_list('alumno_id', flat=True).distinct()

        alumnos_calif_list = []

        for alu_id in alumnos_ids:
            promedio_final = Decimal('0.00')
            
            for pond in ponderaciones:
                notas_cat = Calificacion.objects.filter(alumno_id=alu_id, actividad__ponderacion=pond)
                if notas_cat.exists():
                    prom_cat = notas_cat.aggregate(Avg('valor'))['valor__avg'] or Decimal('0.00')
                    promedio_final += (prom_cat * pond.porcentaje) / Decimal('100')

            # Aplicar redondeo institucional (>= 0.5 sube)
            redondeado = int(promedio_final.quantize(Decimal('1'), rounding=ROUND_HALF_UP))
            
            # Determinar estatus según el promedio redondeado
            estatus = "REPROBADO"
            if redondeado >= 8:
                estatus = "APROBADO"
            elif 6 <= redondeado < 8:
                estatus = "EN_RIESGO"

            # Nota: nombre_completo y matricula deben obtenerse idealmente vía gRPC desde MS-3 
            # antes de retornar esta respuesta. Aquí se envían IDs como placeholder.
            alumnos_calif_list.append(calificaciones_pb2.AlumnoCalif(
                alumno_id=alu_id,
                nombre_completo="Consultar MS-3", 
                promedio_real=float(promedio_final),
                promedio_redondeado=redondeado,
                estatus=estatus
            ))

        return calificaciones_pb2.GetConcentradoResponse(alumnos=alumnos_calif_list)

    def GetPromedioAlumno(self, request, context):
        """Retorna el promedio individual para MS-7 Reportes."""
        materia_id = request.materia_id
        alumno_id = request.alumno_id
        
        ponderaciones = Ponderacion.objects.filter(materia_id=materia_id)
        promedio_final = Decimal('0.00')

        for pond in ponderaciones:
            notas_cat = Calificacion.objects.filter(alumno_id=alumno_id, actividad__ponderacion=pond)
            if notas_cat.exists():
                prom_cat = notas_cat.aggregate(Avg('valor'))['valor__avg'] or Decimal('0.00')
                promedio_final += (prom_cat * pond.porcentaje) / Decimal('100')

        redondeado = int(promedio_final.quantize(Decimal('1'), rounding=ROUND_HALF_UP))

        return calificaciones_pb2.GetPromedioAlumnoResponse(
            alumno_id=alumno_id,
            materia_id=materia_id,
            promedio_real=float(promedio_final),
            promedio_redondeado=redondeado
        )

    def GetEstadisticasMateria(self, request, context):
        """Genera métricas de rendimiento grupal."""
        materia_id = request.materia_id
        qs = Calificacion.objects.filter(actividad__ponderacion__materia_id=materia_id)
        
        if not qs.exists():
            return calificaciones_pb2.GetEstadisticasMateriaResponse(materia_id=materia_id)

        # Usamos la lógica de GetConcentrado para contar por estatus
        # En un proyecto real, se optimizaría con agregaciones de BD
        concentrado = self.GetConcentrado(request, context)
        
        aprobados = sum(1 for a in concentrado.alumnos if a.estatus == "APROBADO")
        reprobados = sum(1 for a in concentrado.alumnos if a.estatus == "REPROBADO")
        en_riesgo = sum(1 for a in concentrado.alumnos if a.estatus == "EN_RIESGO")
        
        promedio_grupal = qs.aggregate(Avg('valor'))['valor__avg'] or 0
        val_max = qs.aggregate(Max('valor'))['valor__max'] or 0
        val_min = qs.aggregate(Min('valor'))['valor__min'] or 0

        return calificaciones_pb2.GetEstadisticasMateriaResponse(
            materia_id=materia_id,
            total_alumnos=len(concentrado.alumnos),
            aprobados=aprobados,
            reprobados=reprobados,
            en_riesgo=en_riesgo,
            promedio_grupal=float(promedio_grupal),
            calificacion_maxima=float(val_max),
            calificacion_minima=float(val_min)
        )