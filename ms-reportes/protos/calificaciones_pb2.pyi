from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetConcentradoRequest(_message.Message):
    __slots__ = ("materia_id",)
    MATERIA_ID_FIELD_NUMBER: _ClassVar[int]
    materia_id: str
    def __init__(self, materia_id: _Optional[str] = ...) -> None: ...

class AlumnoCalif(_message.Message):
    __slots__ = ("alumno_id", "matricula", "nombre_completo", "promedio_real", "promedio_redondeado", "estado")
    ALUMNO_ID_FIELD_NUMBER: _ClassVar[int]
    MATRICULA_FIELD_NUMBER: _ClassVar[int]
    NOMBRE_COMPLETO_FIELD_NUMBER: _ClassVar[int]
    PROMEDIO_REAL_FIELD_NUMBER: _ClassVar[int]
    PROMEDIO_REDONDEADO_FIELD_NUMBER: _ClassVar[int]
    ESTADO_FIELD_NUMBER: _ClassVar[int]
    alumno_id: str
    matricula: str
    nombre_completo: str
    promedio_real: float
    promedio_redondeado: int
    estado: str
    def __init__(self, alumno_id: _Optional[str] = ..., matricula: _Optional[str] = ..., nombre_completo: _Optional[str] = ..., promedio_real: _Optional[float] = ..., promedio_redondeado: _Optional[int] = ..., estado: _Optional[str] = ...) -> None: ...

class ConcentradoResponse(_message.Message):
    __slots__ = ("alumnos",)
    ALUMNOS_FIELD_NUMBER: _ClassVar[int]
    alumnos: _containers.RepeatedCompositeFieldContainer[AlumnoCalif]
    def __init__(self, alumnos: _Optional[_Iterable[_Union[AlumnoCalif, _Mapping]]] = ...) -> None: ...

class GetPromedioAlumnoRequest(_message.Message):
    __slots__ = ("alumno_id", "materia_id")
    ALUMNO_ID_FIELD_NUMBER: _ClassVar[int]
    MATERIA_ID_FIELD_NUMBER: _ClassVar[int]
    alumno_id: str
    materia_id: str
    def __init__(self, alumno_id: _Optional[str] = ..., materia_id: _Optional[str] = ...) -> None: ...

class PromedioResponse(_message.Message):
    __slots__ = ("promedio_real", "promedio_redondeado")
    PROMEDIO_REAL_FIELD_NUMBER: _ClassVar[int]
    PROMEDIO_REDONDEADO_FIELD_NUMBER: _ClassVar[int]
    promedio_real: float
    promedio_redondeado: int
    def __init__(self, promedio_real: _Optional[float] = ..., promedio_redondeado: _Optional[int] = ...) -> None: ...

class GetEstadisticasMateriaRequest(_message.Message):
    __slots__ = ("materia_id",)
    MATERIA_ID_FIELD_NUMBER: _ClassVar[int]
    materia_id: str
    def __init__(self, materia_id: _Optional[str] = ...) -> None: ...

class EstadisticasMateria(_message.Message):
    __slots__ = ("materia_id", "total_alumnos", "aprobados", "reprobados", "promedio_grupal", "calificacion_maxima", "calificacion_minima")
    MATERIA_ID_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ALUMNOS_FIELD_NUMBER: _ClassVar[int]
    APROBADOS_FIELD_NUMBER: _ClassVar[int]
    REPROBADOS_FIELD_NUMBER: _ClassVar[int]
    PROMEDIO_GRUPAL_FIELD_NUMBER: _ClassVar[int]
    CALIFICACION_MAXIMA_FIELD_NUMBER: _ClassVar[int]
    CALIFICACION_MINIMA_FIELD_NUMBER: _ClassVar[int]
    materia_id: str
    total_alumnos: int
    aprobados: int
    reprobados: int
    promedio_grupal: float
    calificacion_maxima: float
    calificacion_minima: float
    def __init__(self, materia_id: _Optional[str] = ..., total_alumnos: _Optional[int] = ..., aprobados: _Optional[int] = ..., reprobados: _Optional[int] = ..., promedio_grupal: _Optional[float] = ..., calificacion_maxima: _Optional[float] = ..., calificacion_minima: _Optional[float] = ...) -> None: ...
