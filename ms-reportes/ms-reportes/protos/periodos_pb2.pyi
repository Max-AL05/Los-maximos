from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EmptyRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetMateriaByIdRequest(_message.Message):
    __slots__ = ("materia_id",)
    MATERIA_ID_FIELD_NUMBER: _ClassVar[int]
    materia_id: str
    def __init__(self, materia_id: _Optional[str] = ...) -> None: ...

class MateriaInfo(_message.Message):
    __slots__ = ("materia_id", "nrc", "nombre", "seccion", "clave", "docente_id", "horario", "periodo_id", "estado")
    MATERIA_ID_FIELD_NUMBER: _ClassVar[int]
    NRC_FIELD_NUMBER: _ClassVar[int]
    NOMBRE_FIELD_NUMBER: _ClassVar[int]
    SECCION_FIELD_NUMBER: _ClassVar[int]
    CLAVE_FIELD_NUMBER: _ClassVar[int]
    DOCENTE_ID_FIELD_NUMBER: _ClassVar[int]
    HORARIO_FIELD_NUMBER: _ClassVar[int]
    PERIODO_ID_FIELD_NUMBER: _ClassVar[int]
    ESTADO_FIELD_NUMBER: _ClassVar[int]
    materia_id: str
    nrc: str
    nombre: str
    seccion: str
    clave: str
    docente_id: str
    horario: str
    periodo_id: str
    estado: str
    def __init__(self, materia_id: _Optional[str] = ..., nrc: _Optional[str] = ..., nombre: _Optional[str] = ..., seccion: _Optional[str] = ..., clave: _Optional[str] = ..., docente_id: _Optional[str] = ..., horario: _Optional[str] = ..., periodo_id: _Optional[str] = ..., estado: _Optional[str] = ...) -> None: ...

class GetMateriasByDocenteRequest(_message.Message):
    __slots__ = ("docente_id", "periodo_id")
    DOCENTE_ID_FIELD_NUMBER: _ClassVar[int]
    PERIODO_ID_FIELD_NUMBER: _ClassVar[int]
    docente_id: str
    periodo_id: str
    def __init__(self, docente_id: _Optional[str] = ..., periodo_id: _Optional[str] = ...) -> None: ...

class MateriasList(_message.Message):
    __slots__ = ("materias",)
    MATERIAS_FIELD_NUMBER: _ClassVar[int]
    materias: _containers.RepeatedCompositeFieldContainer[MateriaInfo]
    def __init__(self, materias: _Optional[_Iterable[_Union[MateriaInfo, _Mapping]]] = ...) -> None: ...

class PeriodoInfo(_message.Message):
    __slots__ = ("periodo_id", "nombre", "fecha_inicio", "fecha_fin", "plan_estudios", "activo")
    PERIODO_ID_FIELD_NUMBER: _ClassVar[int]
    NOMBRE_FIELD_NUMBER: _ClassVar[int]
    FECHA_INICIO_FIELD_NUMBER: _ClassVar[int]
    FECHA_FIN_FIELD_NUMBER: _ClassVar[int]
    PLAN_ESTUDIOS_FIELD_NUMBER: _ClassVar[int]
    ACTIVO_FIELD_NUMBER: _ClassVar[int]
    periodo_id: str
    nombre: str
    fecha_inicio: str
    fecha_fin: str
    plan_estudios: str
    activo: bool
    def __init__(self, periodo_id: _Optional[str] = ..., nombre: _Optional[str] = ..., fecha_inicio: _Optional[str] = ..., fecha_fin: _Optional[str] = ..., plan_estudios: _Optional[str] = ..., activo: bool = ...) -> None: ...
