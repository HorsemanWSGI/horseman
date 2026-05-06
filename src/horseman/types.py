from typing import Any
from types import TracebackType
from collections.abc import MutableMapping, Sequence, Iterable, Callable
from horseman.abc.response import ResponseProtocol
from kettu.types import StatusCode


WSGIEnviron = MutableMapping[str, Any]
ExceptionInfo = (
    tuple[type[BaseException], BaseException, TracebackType] |
    tuple[None, None, None] |
    None
)
ResponseHeaders = Sequence[tuple[str | bytes, str | bytes]]
StartResponse = Callable[
    [StatusCode, ResponseHeaders, ExceptionInfo],
    Callable[[bytes], None] | None,
]
WSGICallable = Callable[[WSGIEnviron, StartResponse], Iterable[bytes]]
Finisher = Callable[[ResponseProtocol], None]
