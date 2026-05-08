from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GenerateReportRequest(_message.Message):
    __slots__ = ("tipo", "formato", "materia_id")
    TIPO_FIELD_NUMBER: _ClassVar[int]
    FORMATO_FIELD_NUMBER: _ClassVar[int]
    MATERIA_ID_FIELD_NUMBER: _ClassVar[int]
    tipo: str
    formato: str
    materia_id: str
    def __init__(self, tipo: _Optional[str] = ..., formato: _Optional[str] = ..., materia_id: _Optional[str] = ...) -> None: ...

class FileResponse(_message.Message):
    __slots__ = ("file_bytes", "file_name", "mime_type")
    FILE_BYTES_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    MIME_TYPE_FIELD_NUMBER: _ClassVar[int]
    file_bytes: bytes
    file_name: str
    mime_type: str
    def __init__(self, file_bytes: _Optional[bytes] = ..., file_name: _Optional[str] = ..., mime_type: _Optional[str] = ...) -> None: ...

class GetHistorialDocenteRequest(_message.Message):
    __slots__ = ("docente_id",)
    DOCENTE_ID_FIELD_NUMBER: _ClassVar[int]
    docente_id: str
    def __init__(self, docente_id: _Optional[str] = ...) -> None: ...

class StatsPeriodo(_message.Message):
    __slots__ = ("periodo_id", "periodo_nombre", "materia_id", "materia_nombre", "total_alumnos", "promedio_grupal", "porcentaje_asistencia")
    PERIODO_ID_FIELD_NUMBER: _ClassVar[int]
    PERIODO_NOMBRE_FIELD_NUMBER: _ClassVar[int]
    MATERIA_ID_FIELD_NUMBER: _ClassVar[int]
    MATERIA_NOMBRE_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ALUMNOS_FIELD_NUMBER: _ClassVar[int]
    PROMEDIO_GRUPAL_FIELD_NUMBER: _ClassVar[int]
    PORCENTAJE_ASISTENCIA_FIELD_NUMBER: _ClassVar[int]
    periodo_id: str
    periodo_nombre: str
    materia_id: str
    materia_nombre: str
    total_alumnos: int
    promedio_grupal: float
    porcentaje_asistencia: float
    def __init__(self, periodo_id: _Optional[str] = ..., periodo_nombre: _Optional[str] = ..., materia_id: _Optional[str] = ..., materia_nombre: _Optional[str] = ..., total_alumnos: _Optional[int] = ..., promedio_grupal: _Optional[float] = ..., porcentaje_asistencia: _Optional[float] = ...) -> None: ...

class HistorialResponse(_message.Message):
    __slots__ = ("historial",)
    HISTORIAL_FIELD_NUMBER: _ClassVar[int]
    historial: _containers.RepeatedCompositeFieldContainer[StatsPeriodo]
    def __init__(self, historial: _Optional[_Iterable[_Union[StatsPeriodo, _Mapping]]] = ...) -> None: ...
