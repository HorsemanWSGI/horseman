from http import HTTPStatus
from types import TracebackType
from typing import (
    Any,
    ByteString,
    Callable,
    Iterable,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Literal
)


MIMEType = TypeVar('MIMEType', str, bytes)
HTTPCode = TypeVar('HTTPCode', HTTPStatus, int)
StatusCode = TypeVar('StatusCode', str, bytes)

Environ = Mapping[str, Any]
ExceptionInfo = Tuple[Exception, Any, TracebackType]
ResponseHeaders = Sequence[Tuple[str, str]]
StartResponse = Callable[
    [StatusCode, ResponseHeaders, Optional[ExceptionInfo]],
    Optional[Callable[[ByteString], None]]
]

URLParameter = TypeVar('URLParameter')
WSGICallable = Callable[[Environ, StartResponse], Iterable[bytes]]
HTTPMethod = Literal[
    "GET", "HEAD", "PUT", "DELETE", "PATCH", "POST", "OPTIONS"
]
