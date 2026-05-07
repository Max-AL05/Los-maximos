from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ValidateTokenRequest(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: str
    def __init__(self, token: _Optional[str] = ...) -> None: ...

class UserClaims(_message.Message):
    __slots__ = ("user_id", "email", "role", "is_valid", "exp")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    IS_VALID_FIELD_NUMBER: _ClassVar[int]
    EXP_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    email: str
    role: str
    is_valid: bool
    exp: int
    def __init__(self, user_id: _Optional[str] = ..., email: _Optional[str] = ..., role: _Optional[str] = ..., is_valid: bool = ..., exp: _Optional[int] = ...) -> None: ...

class GetUserByIdRequest(_message.Message):
    __slots__ = ("user_id",)
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    def __init__(self, user_id: _Optional[str] = ...) -> None: ...

class UserProfile(_message.Message):
    __slots__ = ("user_id", "email", "nombre_completo", "role", "is_active")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    NOMBRE_COMPLETO_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    email: str
    nombre_completo: str
    role: str
    is_active: bool
    def __init__(self, user_id: _Optional[str] = ..., email: _Optional[str] = ..., nombre_completo: _Optional[str] = ..., role: _Optional[str] = ..., is_active: bool = ...) -> None: ...

class CheckRoleRequest(_message.Message):
    __slots__ = ("user_id", "role")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    role: str
    def __init__(self, user_id: _Optional[str] = ..., role: _Optional[str] = ...) -> None: ...

class CheckRoleResponse(_message.Message):
    __slots__ = ("has_role",)
    HAS_ROLE_FIELD_NUMBER: _ClassVar[int]
    has_role: bool
    def __init__(self, has_role: bool = ...) -> None: ...
