"""
Cliente gRPC hacia MS-3 Alumnos.

Implementa los tres métodos del contrato `proto/alumnos.proto`:
    - GetAlumnoById          (uno)
    - GetAlumnosByMateria    (lote – usado por el concentrado para evitar N+1)
    - IsAlumnoEnMateria

Mapea cada respuesta del proto a un dict simple para que la capa de servicios
no dependa directamente de los stubs generados.
"""
import logging

import grpc
from django.conf import settings

import protos.alumnos_pb2 as alumnos_pb2
import protos.alumnos_pb2_grpc as alumnos_pb2_grpc


logger = logging.getLogger(__name__)


# Forma "vacía" cuando MS-3 no responde. Permite que el concentrado siga
# generándose con los IDs aunque no tengamos los nombres reales.
_FALLBACK_ALUMNO = {
    "alumno_id":       "",
    "nombre_completo": "Alumno no disponible",
    "matricula":       "N/A",
    "correo":          "",
    "tipo_formacion":  "",
    "activo_en_materia": True,
}


def _claim_dict(c) -> dict:
    """
    Convierte un mensaje proto AlumnoInfo a dict.

    Los nombres de campo siguen EXACTAMENTE el contrato `alumnos.proto`:
        alumno_id, matricula, nombre_completo, correo, tipo_formacion,
        activo_en_materia.

    Cualquier desviación de estos nombres rompe el mapeo en silencio
    porque el proto no falla — solo regresa string vacío para campos
    inexistentes. Por eso este wrapper centralizado: si algún día cambia
    el .proto, basta tocar aquí.
    """
    return {
        "alumno_id":         c.alumno_id,
        "matricula":         c.matricula,
        "nombre_completo":   c.nombre_completo,
        "correo":            c.correo,
        "tipo_formacion":    c.tipo_formacion,
        "activo_en_materia": c.activo_en_materia,
    }


class AlumnosClient:
    """
    Cliente sincrónico de MS-3.

    Reusa el canal entre llamadas. Cada RPC tiene timeout y maneja
    grpc.RpcError de forma consistente — devuelve datos placeholder cuando
    el caller (services.py) no quiere que el endpoint REST falle por un
    fallo transitorio de MS-3.
    """

    def __init__(self, target: str | None = None, timeout: float | None = None):
        self.target = target or settings.GRPC_TARGETS["alumnos"]
        self.timeout = timeout if timeout is not None else settings.GRPC_DEFAULT_TIMEOUT
        self.channel = grpc.insecure_channel(self.target)
        self.stub = alumnos_pb2_grpc.AlumnosServiceStub(self.channel)

    # ───────────────────────────── API pública ──────────────────────────────

    def obtener_alumnos_de_materia(self, materia_id: str, *, solo_activos: bool = True) -> list[dict]:
        """
        Trae el listado completo de inscritos de una materia (1 sola RPC).

        Si `solo_activos=True` (default) descarta los dados de baja
        leyendo el campo `activo_en_materia` del contrato.
        """
        try:
            req = alumnos_pb2.GetAlumnosByMateriaRequest(materia_id=materia_id)
            resp = self.stub.GetAlumnosByMateria(req, timeout=self.timeout)
            alumnos = [_claim_dict(a) for a in resp.alumnos]
            if solo_activos:
                alumnos = [a for a in alumnos if a["activo_en_materia"]]
            return alumnos
        except grpc.RpcError as e:
            logger.warning(
                "[alumnos_client] GetAlumnosByMateria(%s) falló: %s",
                materia_id, e,
            )
            return []

    def obtener_datos_alumno(self, alumno_id: str) -> dict:
        """
        Versión 1-a-1 (compatible con el código previo).

        IMPORTANTE: si vas a iterar sobre N alumnos usa
        `obtener_alumnos_de_materia` para evitar N llamadas gRPC.
        """
        try:
            req = alumnos_pb2.GetAlumnoByIdRequest(alumno_id=alumno_id)
            resp = self.stub.GetAlumnoById(req, timeout=self.timeout)
            return _claim_dict(resp)
        except grpc.RpcError as e:
            logger.warning(
                "[alumnos_client] GetAlumnoById(%s) falló: %s",
                alumno_id, e,
            )
            return {**_FALLBACK_ALUMNO, "alumno_id": alumno_id}

    def esta_inscrito(self, alumno_id: str, materia_id: str) -> tuple[bool, bool]:
        """
        Devuelve (inscrito, dado_de_baja) según el contrato.
        """
        try:
            req = alumnos_pb2.IsAlumnoEnMateriaRequest(
                alumno_id=alumno_id, materia_id=materia_id,
            )
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