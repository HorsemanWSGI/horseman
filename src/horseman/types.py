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
    Literal,
)

HTTPMethod = Literal[
    "GET", "HEAD", "PUT", "DELETE", "PATCH", "POST", "OPTIONS"
]

Charset = TypeVar('Charset', str, bytes)
MIMEType = TypeVar('MIMEType', str, bytes)
HTTPCode = TypeVar('HTTPCode', HTTPStatus, int)
StatusCode = TypeVar('StatusCode', str, bytes)
URLParameter = TypeVar('URLParameter')

Environ = Mapping[str, Any]
ExceptionInfo = Tuple[Exception, Any, TracebackType]
ResponseHeaders = Sequence[Tuple[str, str]]
StartResponse = Callable[
    [StatusCode, ResponseHeaders, Optional[ExceptionInfo]],
    Optional[Callable[[ByteString], None]]
]
WSGICallable = Callable[[Environ, StartResponse], Iterable[bytes]]
