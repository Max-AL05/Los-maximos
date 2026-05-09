import grpc
import protos.alumnos_pb2 as alumnos_pb2
import protos.alumnos_pb2_grpc as alumnos_pb2_grpc
from django.conf import settings

class AlumnosClient:
    def __init__(self):
        # Leemos el host del .env, por defecto localhost si no existe
        host = getattr(settings, 'MS_ALUMNOS_HOST', 'localhost')
        # Puerto 50053 para el MS-3
        self.channel = grpc.insecure_channel(f"{host}:50053")
        self.stub = alumnos_pb2_grpc.AlumnosServiceStub(self.channel)

    def obtener_datos_alumno(self, alumno_id):
        """
        Consulta al MS-3 usando GetAlumnoById.
        Retorna la información completa del mensaje AlumnoInfo.
        """
        try:
            # Coincidimos con: GetAlumnoByIdRequest
            request = alumnos_pb2.GetAlumnoByIdRequest(alumno_id=alumno_id)
            # Llamada al método rpc GetAlumnoById
            response = self.stub.GetAlumnoById(request)
            
            return {
                "nombre": response.nombre_completo,
                "matricula": response.matricula,
                "correo": response.correo,
                "success": True
            }
        except grpc.RpcError as e:
            print(f"[MS-4] Error de conexión con MS-3 Alumnos: {e.details()}")
            return {
                "nombre": "Nombre no disponible",
                "matricula": "N/A",
                "correo": "N/A",
                "success": False
            }