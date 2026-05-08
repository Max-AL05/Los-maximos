from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetAsistenciaAlumnoRequest(_message.Message):
    __slots__ = ("alumno_id", "materia_id")
    ALUMNO_ID_FIELD_NUMBER: _ClassVar[int]
    MATERIA_ID_FIELD_NUMBER: _ClassVar[int]
    alumno_id: str
    materia_id: str
    def __init__(self, alumno_id: _Optional[str] = ..., materia_id: _Optional[str] = ...) -> None: ...

class Asistencia(_message.Message):
    __slots__ = ("asistencia_id", "fecha", "estado", "sesion_id")
    ASISTENCIA_ID_FIELD_NUMBER: _ClassVar[int]
    FECHA_FIELD_NUMBER: _ClassVar[int]
    ESTADO_FIELD_NUMBER: _ClassVar[int]
    SESION_ID_FIELD_NUMBER: _ClassVar[int]
    asistencia_id: str
    fecha: str
    estado: str
    sesion_id: str
    def __init__(self, asistencia_id: _Optional[str] = ..., fecha: _Optional[str] = ..., estado: _Optional[str] = ..., sesion_id: _Optional[str] = ...) -> None: ...

class AsistenciasList(_message.Message):
    __slots__ = ("asistencias",)
    ASISTENCIAS_FIELD_NUMBER: _ClassVar[int]
    asistencias: _containers.RepeatedCompositeFieldContainer[Asistencia]
    def __init__(self, asistencias: _Optional[_Iterable[_Union[Asistencia, _Mapping]]] = ...) -> None: ...

class GetEstadisticasAsistenciaRequest(_message.Message):
    __slots__ = ("materia_id",)
    MATERIA_ID_FIELD_NUMBER: _ClassVar[int]
    materia_id: str
    def __init__(self, materia_id: _Optional[str] = ...) -> None: ...

class EstadisticasAsistencia(_message.Message):
    __slots__ = ("materia_id", "total_sesiones", "total_asistencias", "total_retardos", "total_ausencias", "porcentaje_asistencia")
    MATERIA_ID_FIELD_NUMBER: _ClassVar[int]
    TOTAL_SESIONES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ASISTENCIAS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_RETARDOS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_AUSENCIAS_FIELD_NUMBER: _ClassVar[int]
    PORCENTAJE_ASISTENCIA_FIELD_NUMBER: _ClassVar[int]
    materia_id: str
    total_sesiones: int
    total_asistencias: int
    total_retardos: int
    total_ausencias: int
    porcentaje_asistencia: float
    def __init__(self, materia_id: _Optional[str] = ..., total_sesiones: _Optional[int] = ..., total_asistencias: _Optional[int] = ..., total_retardos: _Optional[int] = ..., total_ausencias: _Optional[int] = ..., porcentaje_asistencia: _Optional[float] = ...) -> None: ...
