import orjson
from http import HTTPStatus
from horseman.http import Cookies
from horseman.types import Environ, HTTPCode, StartResponse
from typing import Any, Generator, Iterable, Optional, Tuple


BODYLESS = frozenset((
    HTTPStatus.CONTINUE,
    HTTPStatus.SWITCHING_PROTOCOLS,
    HTTPStatus.PROCESSING,
    HTTPStatus.NO_CONTENT,
    HTTPStatus.NOT_MODIFIED
))

REDIRECT = frozenset((
    HTTPStatus.MULTIPLE_CHOICES,
    HTTPStatus.MOVED_PERMANENTLY,
    HTTPStatus.FOUND,
    HTTPStatus.SEE_OTHER,
    HTTPStatus.NOT_MODIFIED,
    HTTPStatus.USE_PROXY,
    HTTPStatus.TEMPORARY_REDIRECT,
    HTTPStatus.PERMANENT_REDIRECT
))


def file_iterator(path, chunk=4096):
    with open(path, 'rb') as reader:
        while True:
            data = reader.read(chunk)
            if not data:
                break
            yield data


class Response:

    def __init__(self, status: HTTPCode,
                 body: Iterable, headers: Optional[dict]):
        self.status = HTTPStatus(status)
        self.body = body
        self.headers = headers or {}
        self._cookies = None

    @property
    def cookies(self):
        if self._cookies is None:
            self._cookies = Cookies()
        return self._cookies

    def headers_pair(self) -> Generator[Tuple[str, str], None, None]:
        for key, value in self.headers.items():
            yield key, str(value)
        if self._cookies:
            for cookie in self._cookies.values():
                yield 'Set-Cookie', str(cookie)

    def __iter__(self) -> Generator[bytes, None, None]:
        if self.status not in BODYLESS:
            if self.body is None:
                yield self.status.description.encode()
            elif isinstance(self.body, bytes):
                yield self.body
            elif isinstance(self.body, str):
                yield self.body.encode()
            elif isinstance(self.body, Generator):
                yield from self.body
            else:
                raise TypeError(
                    f'Body of type {type(self.body)!r} is not supported.'
                )

    def __call__(self, environ: Environ,
                 start_response: StartResponse) -> Iterable:
        status = f'{self.status.value} {self.status.phrase}'
        start_response(status, list(self.headers_pair()))
        return self

    @classmethod
    def create(cls, code: HTTPCode = 200, body: Optional[Iterable] = None,
               headers: Optional[dict] = None):
        return cls(code, body, headers)

    @classmethod
    def redirect(cls, location, code: HTTPCode = 303,
                 body: Optional[Iterable] = None,
                 headers: Optional[dict] = None):
        if not code in REDIRECT:
            raise ValueError(f"{code}: unknown redirection code.")
        if not headers:
            headers = {'Location': location}
        else:
            headers['Location'] = location
        return cls(code, body, headers)

    @classmethod
    def from_file_iterator(cls, filename: str, body: Iterable[bytes],
                           headers: Optional[dict] = None):
        if headers is None:
            headers = {
                "Content-Disposition": f"attachment;filename={filename}"}
        elif "Content-Disposition" not in headers:
            headers["Content-Disposition"] = (
                f"attachment;filename={filename}")
        return cls(200, body, headers)

    @classmethod
    def to_json(cls, code: HTTPCode = 200, body: Optional[Any] = None,
                headers: Optional[dict] = None):
        data = orjson.dumps(body)
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        else:
            headers['Content-Type'] = 'application/json'
        return cls(code, data, headers)

    @classmethod
    def from_json(cls, code: HTTPCode = 200, body: str = '',
                  headers: Optional[dict] = None):
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        else:
            headers['Content-Type'] = 'application/json'
        return cls(code, body, headers)


reply = Response.create
redirect = Response.redirect
