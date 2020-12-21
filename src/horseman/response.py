from http import HTTPStatus
from horseman.http import Multidict, Cookies
from horseman.prototyping import Environ, HTTPCode, StartResponse
from typing import Any, Generator, Iterable, Optional, Tuple
try:
    # In case you use json heavily, we recommend installing
    # https://pypi.python.org/pypi/ujson for better performances.
    import ujson as json
except ImportError:
    import json as json


BODYLESS = frozenset((
    HTTPStatus.CONTINUE,
    HTTPStatus.SWITCHING_PROTOCOLS,
    HTTPStatus.PROCESSING,
    HTTPStatus.NO_CONTENT,
    HTTPStatus.NOT_MODIFIED
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
        self.headers = Multidict(headers or {})
        self._cookies = None

    @property
    def cookies(self):
        if self._cookies is None:
            self._cookies = Cookies()
        return self._cookies

    def headers_pair(self) -> Generator[Tuple[str, str], None, None]:
        for key, value in self.headers.items():
            yield key, str(value)

    def __call__(self, environ: Environ,
                 start_response: StartResponse) -> Iterable:
        status = f'{self.status.value} {self.status.phrase}'
        start_response(status, list(self.headers_pair()))
        if self.status not in BODYLESS:
            if self.body is None:
                return [self.status.description.encode()]
            if isinstance(self.body, bytes):
                return [self.body]
            elif isinstance(self.body, str):
                return [self.body.encode()]
            else:
                return self.body
        return []

    @classmethod
    def create(cls, code: HTTPCode = 200, body: Optional[Iterable] = None,
               headers: Optional[dict] = None):
        return cls(code, body, headers)

    @classmethod
    def to_json(cls, code: HTTPCode = 200, body: Optional[Any] = None,
                headers: Optional[dict] = None):
        data = json.dumps(body)
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
