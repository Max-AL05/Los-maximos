from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetAlumnosByMateriaRequest(_message.Message):
    __slots__ = ("materia_id",)
    MATERIA_ID_FIELD_NUMBER: _ClassVar[int]
    materia_id: str
    def __init__(self, materia_id: _Optional[str] = ...) -> None: ...

class AlumnoInfo(_message.Message):
    __slots__ = ("alumno_id", "matricula", "nombre_completo", "correo", "tipo_formacion", "activo_en_materia")
    ALUMNO_ID_FIELD_NUMBER: _ClassVar[int]
    MATRICULA_FIELD_NUMBER: _ClassVar[int]
    NOMBRE_COMPLETO_FIELD_NUMBER: _ClassVar[int]
    CORREO_FIELD_NUMBER: _ClassVar[int]
    TIPO_FORMACION_FIELD_NUMBER: _ClassVar[int]
    ACTIVO_EN_MATERIA_FIELD_NUMBER: _ClassVar[int]
    alumno_id: str
    matricula: str
    nombre_completo: str
    correo: str
    tipo_formacion: str
    activo_en_materia: bool
    def __init__(self, alumno_id: _Optional[str] = ..., matricula: _Optional[str] = ..., nombre_completo: _Optional[str] = ..., correo: _Optional[str] = ..., tipo_formacion: _Optional[str] = ..., activo_en_materia: bool = ...) -> None: ...

class AlumnosList(_message.Message):
    __slots__ = ("alumnos",)
    ALUMNOS_FIELD_NUMBER: _ClassVar[int]
    alumnos: _containers.RepeatedCompositeFieldContainer[AlumnoInfo]
    def __init__(self, alumnos: _Optional[_Iterable[_Union[AlumnoInfo, _Mapping]]] = ...) -> None: ...

class GetAlumnoByIdRequest(_message.Message):
    __slots__ = ("alumno_id",)
    ALUMNO_ID_FIELD_NUMBER: _ClassVar[int]
    alumno_id: str
    def __init__(self, alumno_id: _Optional[str] = ...) -> None: ...

class IsAlumnoEnMateriaRequest(_message.Message):
    __slots__ = ("alumno_id", "materia_id")
    ALUMNO_ID_FIELD_NUMBER: _ClassVar[int]
    MATERIA_ID_FIELD_NUMBER: _ClassVar[int]
    alumno_id: str
    materia_id: str
    def __init__(self, alumno_id: _Optional[str] = ..., materia_id: _Optional[str] = ...) -> None: ...

class IsAlumnoEnMateriaResponse(_message.Message):
    __slots__ = ("inscrito", "dado_de_baja")
    INSCRITO_FIELD_NUMBER: _ClassVar[int]
    DADO_DE_BAJA_FIELD_NUMBER: _ClassVar[int]
    inscrito: bool
    dado_de_baja: bool
    def __init__(self, inscrito: bool = ..., dado_de_baja: bool = ...) -> None: ...
