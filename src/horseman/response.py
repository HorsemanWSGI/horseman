import inspect
from http import HTTPStatus
from collections.abc import Iterable
from multidict import CIMultiDict
from horseman import HTTPCode
from typing import Iterable, Callable, TypeVar


BODYLESS = frozenset((
    HTTPStatus.CONTINUE,
    HTTPStatus.SWITCHING_PROTOCOLS,
    HTTPStatus.PROCESSING,
    HTTPStatus.NO_CONTENT,
    HTTPStatus.NOT_MODIFIED
))


Headers = TypeVar('headers', dict, None)


class Response:

    __slots__ = ('status', 'body', 'headers')

    def __init__(self, status: HTTPCode, body, headers: Headers):
        self.status = HTTPStatus(status)
        self.body = body
        self.headers = CIMultiDict(headers is None and {} or headers)

    def headers_pair(self):
        if not inspect.isgenerator(self.body) and self.status not in BODYLESS:
            if 'Content-Length' not in self.headers:
                yield 'Content-Length', str(len(self.body))
        for key, value in self.headers.items():
            yield key, str(value)

    def __call__(self, environ: dict, start_response: Callable) -> Iterable:
        status = '{0} {1}'.format(self.status.value, self.status.phrase)
        start_response(status, list(self.headers_pair()))
        if self.status not in BODYLESS:
            if self.body is None:
                return [self.status.description.encode()]
            if isinstance(self.body, bytes):
                return [self.body]
            elif isinstance(self.body, str):
                return [self.body.encode()]
            return self.body
        return []

    @classmethod
    def create(cls, code: HTTPCode, body: Iterable, headers: Headers):
        status = HTTPStatus(code)
        return Response(code, body, headers)


GenericError = Response(
    500,
    'An unexpected error occured. Please contact the administrator.',
    headers={'Content-Type': 'text/plain'}
)


def reply(code: HTTPCode=200, body: Iterable=None, headers: Headers=None):
    return Response.create(code, body, headers)
