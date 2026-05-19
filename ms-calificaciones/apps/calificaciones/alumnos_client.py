import logging
import grpc
from django.conf import settings
import protos.alumnos_pb2 as alumnos_pb2
import protos.alumnos_pb2_grpc as alumnos_pb2_grpc

logger = logging.getLogger(__name__)

_FALLBACK_ALUMNO = {
    "alumno_id":       "",
    "nombre_completo": "Alumno no disponible",
    "matricula":       "N/A",
    "correo":          "",
    "tipo_formacion":  "",
    "activo_en_materia": True,
}

def _claim_dict(c) -> dict:
    return {
        "alumno_id":         c.alumno_id,
        "matricula":         c.matricula,
        "nombre_completo":   c.nombre_completo,
        "correo":            c.correo,
        "tipo_formacion":    c.tipo_formacion,
        "activo_en_materia": c.activo_en_materia,
    }

class AlumnosClient:
    def __init__(self, target: str | None = None, timeout: float | None = None):
        self.target = target or settings.GRPC_TARGETS["alumnos"]
        self.timeout = timeout if timeout is not None else settings.GRPC_DEFAULT_TIMEOUT
        self.channel = grpc.insecure_channel(self.target)
        self.stub = alumnos_pb2_grpc.AlumnosServiceStub(self.channel)

    def obtener_alumnos_de_materia(self, materia_id: str, *, solo_activos: bool = True) -> list[dict]:
        try:
            req = alumnos_pb2.GetAlumnosByMateriaRequest(materia_id=materia_id)
            resp = self.stub.GetAlumnosByMateria(req, timeout=self.timeout)
            alumnos = [_claim_dict(a) for a in resp.alumnos]
            if solo_activos:
                alumnos = [a for a in alumnos if a["activo_en_materia"]]
            return alumnos
        except grpc.RpcError as e:
            logger.warning("[alumnos_client] GetAlumnosByMateria(%s) falló: %s", materia_id, e)
            return []

    def obtener_datos_alumno(self, alumno_id: str) -> dict:
        try:
            req = alumnos_pb2.GetAlumnoByIdRequest(alumno_id=alumno_id)
            resp = self.stub.GetAlumnoById(req, timeout=self.timeout)
            return _claim_dict(resp)
        except grpc.RpcError as e:
            logger.warning("[alumnos_client] GetAlumnoById(%s) falló: %s", alumno_id, e)
            return {**_FALLBACK_ALUMNO, "alumno_id": alumno_id}

    def esta_inscrito(self, alumno_id: str, materia_id: str) -> tuple[bool, bool]:
        try:
            req = alumnos_pb2.IsAlumnoEnMateriaRequest(alumno_id=alumno_id, materia_id=materia_id)
            resp = self.stub.IsAlumnoEnMateria(req, timeout=self.timeout)
            return resp.inscrito, resp.dado_de_baja
        except grpc.RpcError as e:
            logger.warning("[alumnos_client] IsAlumnoEnMateria falló: %s", e)
            return False, False

    def __del__(self):
        try:
            self.channel.close()
        except Exception:
            pass