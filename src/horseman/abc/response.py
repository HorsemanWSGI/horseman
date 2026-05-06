import orjson
from io import BytesIO
from pathlib import Path
from typing import Generic, TypeVar, AnyStr
from collections.abc import Mapping, Iterable, Iterator, Callable
from http import HTTPStatus
from collections import deque
from kettu.headers import Cookies
from kettu.response import ResponseHeaders
from kettu.constants import EMPTY_STATUSES, REDIRECT_STATUSES
from kettu.types import HTTPCode


BodyT = str | bytes | Iterator[bytes]
HeadersT = Mapping[str, str] | Iterable[tuple[str, str]]
F = TypeVar("F", bound=Callable)


UNSET = object()


class FileResponseProtocol:

    __slots__ = ("status", "block_size", "headers", "file_")

    def __init__(
            self,
            file_: Path | BytesIO,
            status: HTTPCode = 200,
            block_size: int = 4096,
            headers: HeadersT | None = None,
    ):
        self.status = HTTPStatus(status)
        self.file_ = file_
        self.headers = ResponseHeaders(headers)  # idempotent.
        self.block_size = block_size

    @property
    def cookies(self) -> Cookies:
        return self.headers.cookies


class ResponseProtocol(Generic[F]):
    __slots__ = ("status", "body", "headers", "_finishers")

    status: HTTPStatus
    headers: ResponseHeaders
    body: BodyT | None
    _finishers: deque[F] | None

    def __init__(
        self,
        status: HTTPCode = 200,
        body: BodyT | None = None,
        headers: HeadersT | None = None,
    ):
        self.status = HTTPStatus(status)
        self.body = body
        self.headers = ResponseHeaders(headers)  # idempotent.
        self._finishers = None

    def add_finisher(self, task: F):
        if self._finishers is None:
            self._finishers = deque([task])
        else:
            self._finishers.append(task)

    @property
    def cookies(self) -> Cookies:
        return self.headers.cookies

    def __iter__(self) -> Iterator[bytes]:
        if self.status not in EMPTY_STATUSES:
            if self.body is None:
                yield self.status.description.encode()
            elif isinstance(self.body, bytes):
                yield self.body
            elif isinstance(self.body, str):
                yield self.body.encode()
            elif isinstance(self.body, Iterator):
                yield from self.body
            else:
                raise TypeError(
                    f"Body of type {type(self.body)!r} is not supported.")

    @classmethod
    def to_json(
            cls,
            code: HTTPCode = 200,
            body: BodyT | None = None,
            headers: HeadersT | None = None,
    ) -> "ResponseProtocol":
        data = orjson.dumps(body)
        if headers is None:
            headers = {"Content-Type": "application/json"}
        else:
            headers = ResponseHeaders(headers)
            headers["Content-Type"] = "application/json"
        return cls(code, data, headers)

    @classmethod
    def html(
            cls,
            code: HTTPCode = 200,
            body: AnyStr = b"",
            headers: HeadersT | None = None,
    ) -> "ResponseProtocol":
        response = cls(code, body, headers=headers)
        response.headers.content_type = "text/html; charset=utf-8"
        return response

    @classmethod
    def redirect(
            cls,
            location: str | None,
            code: HTTPCode = 303,
            body: BodyT | None = None,
            headers: HeadersT | None = None,
    ) -> "ResponseProtocol":
        if code not in REDIRECT_STATUSES:
            raise ValueError(f"{code}: unknown redirection code.")

        response = cls(code, body, headers=headers)
        if location is not None:
            response.headers.location = location
        return response
