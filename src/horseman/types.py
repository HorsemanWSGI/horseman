from http import HTTPStatus
from types import TracebackType
import typing as t


HTTPMethod = t.Literal[
    "GET", "HEAD", "PUT", "DELETE", "PATCH", "POST", "OPTIONS"
]
HTTPMethods = t.Iterable[HTTPMethod]

Boundary = t.TypeVar('Boundary', str, bytes)
Charset = t.TypeVar('Charset', str, bytes)
MIMEType = t.TypeVar('MIMEType', str, bytes)
HTTPCode = t.TypeVar('HTTPCode', HTTPStatus, int)
StatusCode = t.TypeVar('StatusCode', str, bytes)
URLParameter = t.TypeVar('URLParameter')

Environ = t.Mapping[str, t.Any]
ExceptionInfo = t.Tuple[Exception, t.Any, TracebackType]
ResponseHeaders = t.Iterable[t.Tuple[str, str]]
StartResponse = t.Callable[
    [StatusCode, ResponseHeaders, t.Optional[ExceptionInfo]],
    t.Optional[t.Callable[[t.ByteString], None]]
]
WSGICallable = t.Callable[[Environ, StartResponse], t.Iterable[bytes]]
