from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .models import Actividad, Calificacion
from .services import CalificacionesService
from .serializers import (
    ActividadSerializer,
    CalificacionSerializer,
    ImportarCalificacionesSerializer,
    ConcentradoAlumnoSerializer
)

class ActividadViewSet(viewsets.ModelViewSet):
    """
    CRUD para actividades bajo arquitectura de microservicios
    """
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

class CalificacionViewSet(viewsets.ModelViewSet):
    """
    CRUD para calificaciones individuales
    """
    queryset = Calificacion.objects.all()
    serializer_class = CalificacionSerializer
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

@api_view(["POST"])
@parser_classes([MultiPartParser])
# @permission_classes([IsAuthenticated])
@permission_classes([AllowAny])
def importar_calificaciones(request):
    """
    POST /calificaciones/importar
    Automatiza la importación masiva desde archivos Excel/CSV
    """
    serializer = ImportarCalificacionesSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    actividad_id = serializer.validated_data['actividad_id']
    archivo = request.FILES['archivo_excel']
    
    # Delegamos el procesamiento lógico al Servicio 
    exito, resultado = CalificacionesService.procesar_archivo_masivo(actividad_id, archivo)
    
    if exito:
        return Response({
            "success": True, 
            "data": {"importadas": resultado}, 
            "message": "Proceso de importación masiva finalizado con éxito."
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        "success": False, 
        "message": f"Error técnico al procesar el archivo: {resultado}"
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
# @permission_classes([IsAuthenticated])
@permission_classes([AllowAny])
def concentrado(request, materia_id):
    """
    GET /concentrado/<materia_id>
    Muestra el promedio ponderado real y redondeado por alumno
    Diferencia alumnos aprobados, en riesgo o reprobados
    """
    # Obtenemos los datos calculados desde la capa de servicios
    datos_concentrado = CalificacionesService.obtener_concentrado_detallado(materia_id)
    
    if not datos_concentrado:
        return Response({
            "success": False, 
            "message": "No se encontraron ponderaciones o alumnos para esta materia."
        }, status=status.HTTP_404_NOT_FOUND)

    # El serializador maneja la representación final y el estatus 
    serializer = ConcentradoAlumnoSerializer(datos_concentrado, many=True)
    
    return Response({
        "success": True, 
        "data": serializer.data,
        "message": "Concentrado generado correctamente."
    }, status=status.HTTP_200_OK)