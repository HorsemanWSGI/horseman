from http import HTTPStatus
from collections.abc import Iterable
from multidict import CIMultiDict
from horseman import HTTPCode


BODYLESS = frozenset((
    HTTPStatus.CONTINUE,
    HTTPStatus.SWITCHING_PROTOCOLS,
    HTTPStatus.PROCESSING,
    HTTPStatus.NO_CONTENT,
    HTTPStatus.NOT_MODIFIED
))


class Response:

    __slots__ = ('status', 'body', 'headers')

    def __init__(self, status: HTTPCode, body, headers: dict):
        self.status = HTTPStatus(status)
        self.body = body
        self.headers = CIMultiDict(headers)

    def headers_pair(self):
        for key, value in self.headers.items():
            yield (key, str(value))

    def __call__(self, environ, start_response):
        status = '{0} {1}'.format(self.status.value, self.status.phrase)
        start_response(status, list(self.headers_pair()))
        if self.status not in BODYLESS:
            if self.body is None:
                return [self.status.description.encode()]
            if isinstance(self.body, (str, bytes)):
                if isinstance(self.body, str):
                    return [self.body.encode()]
                return [self.body]
            assert isinstance(self.body, Iterable)
            return self.body
        return []

    @classmethod
    def create(cls, code: HTTPCode=200, body=None, **headers):
        status = HTTPStatus(code)
        return Response(code, body, headers)
    

GenericError = Response(
    500,
    'An unexpected error occured. Please contact the administrator.',
    headers={'Content-Type': 'text/plain'}
)
