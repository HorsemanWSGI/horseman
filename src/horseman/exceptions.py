import typing as t
from http import HTTPStatus
from horseman.types import HTTPCode


class ParsingException(ValueError):
    pass


class HTTPError(Exception):

    def __init__(self,
                 status: HTTPCode,
                 body: t.Optional[t.Union[str, bytes]] = None):
        self.status = HTTPStatus(status)
        body = self.status.description if body is None else body
        if isinstance(body, bytes):
            body = body.decode('utf-8')
        elif not isinstance(body, str):
            raise ValueError('Body must be string or bytes.')
        self.body: str = body

    def __bytes__(self) -> bytes:
        return ('HTTP/1.1 {status} {phrase}\r\n'
                'Content-Length: {length}\r\n\r\n{body}').format(
                    status=self.status.value,
                    phrase=self.status.phrase,
                    length=len(self.body),
                    body=self.body
                ).encode()
