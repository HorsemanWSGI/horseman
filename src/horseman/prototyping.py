from typing import (
    Any, Optional, Callable, Sequence, Mapping, Tuple, ByteString, Iterable)
from typing import TypeVar
from types import TracebackType


StatusCode = TypeVar('StatusCode', str, bytes)
Environ = Mapping[str, Any]
ResponseHeaders = Sequence[Tuple[str, str]]
ExceptionInfo = Optional[Tuple[Exception, Any, TracebackType]]
StartResponse = Callable[
    [StatusCode, ResponseHeaders, ExceptionInfo],
    Optional[Callable[[ByteString], None]]
]
WSGICallable = Callable[[Environ, StartResponse], Iterable[bytes]]
URLParameter = TypeVar('URLParameter')
