from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class SendBienvenidaRequest(_message.Message):
    __slots__ = ("alumno_id", "materia_id", "clave_unica")
    ALUMNO_ID_FIELD_NUMBER: _ClassVar[int]
    MATERIA_ID_FIELD_NUMBER: _ClassVar[int]
    CLAVE_UNICA_FIELD_NUMBER: _ClassVar[int]
    alumno_id: str
    materia_id: str
    clave_unica: str
    def __init__(self, alumno_id: _Optional[str] = ..., materia_id: _Optional[str] = ..., clave_unica: _Optional[str] = ...) -> None: ...

class SendBajaRequest(_message.Message):
    __slots__ = ("alumno_id", "docente_id", "materia_id")
    ALUMNO_ID_FIELD_NUMBER: _ClassVar[int]
    DOCENTE_ID_FIELD_NUMBER: _ClassVar[int]
    MATERIA_ID_FIELD_NUMBER: _ClassVar[int]
    alumno_id: str
    docente_id: str
    materia_id: str
    def __init__(self, alumno_id: _Optional[str] = ..., docente_id: _Optional[str] = ..., materia_id: _Optional[str] = ...) -> None: ...

class SendCierreMateriaRequest(_message.Message):
    __slots__ = ("materia_id",)
    MATERIA_ID_FIELD_NUMBER: _ClassVar[int]
    materia_id: str
    def __init__(self, materia_id: _Optional[str] = ...) -> None: ...

class SendResetPasswordRequest(_message.Message):
    __slots__ = ("user_id", "reset_link")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    RESET_LINK_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    reset_link: str
    def __init__(self, user_id: _Optional[str] = ..., reset_link: _Optional[str] = ...) -> None: ...

class SendResponse(_message.Message):
    __slots__ = ("success", "message", "notificacion_id")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    NOTIFICACION_ID_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    notificacion_id: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ..., notificacion_id: _Optional[str] = ...) -> None: ...
