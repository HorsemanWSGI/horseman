from http import HTTPStatus
from types import TracebackType
import typing as t


HTTPMethod = t.Literal[
    "GET", "HEAD", "PUT", "DELETE", "PATCH", "POST", "OPTIONS"
]
HTTPMethods = t.Iterable[HTTPMethod]

Boundary = t.Union[str, bytes]
Charset = t.Union[str, bytes]
MIMEType = t.Union[str, bytes]
HTTPCode = t.Union[HTTPStatus, int]
StatusCode = t.Union[str, bytes]
URLParameter = t.TypeVar('URLParameter')

Environ = t.MutableMapping[str, t.Any]
ExceptionInfo = t.Union[
    t.Tuple[t.Type[BaseException], BaseException, TracebackType],
    t.Tuple[None, None, None]
]
ResponseHeaders = t.Iterable[t.Tuple[str, str]]
StartResponse = t.Callable[
    [StatusCode, ResponseHeaders, t.Optional[ExceptionInfo]],
    t.Optional[t.Callable[[t.ByteString], None]]
]
WSGICallable = t.Callable[[Environ, StartResponse], t.Iterable[bytes]]
