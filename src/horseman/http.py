import cgi
from http import HTTPStatus
from typing import NamedTuple, Dict, AnyStr
from urllib.parse import parse_qsl
from biscuits import Cookie, parse
from horseman.datastructures import TypeCastingDict
from horseman.types import HTTPCode, MIMEType


class HTTPError(Exception):

    def __init__(self, status: HTTPCode, body: AnyStr = ...):
        self.status = HTTPStatus(status)
        body = self.status.description if body is ... else body
        if isinstance(body, bytes):
            body = body.decode('utf-8')
        elif not isinstance(body, str):
            raise ValueError('Body must be string or bytes.')
        self.body: str = body

    def __bytes__(self):
        return ('HTTP/1.1 {status} {phrase}\r\n'
                'Content-Length: {length}\r\n\r\n{body}').format(
                    status=self.status.value,
                    phrase=self.status.phrase,
                    length=len(self.body),
                    body=self.body
                ).encode()


class ContentType(NamedTuple):
    mimetype: MIMEType
    options: dict

    @classmethod
    def from_http_header(cls, header: str):
        return cls(*cgi.parse_header(header))


class Cookies(Dict[str, Cookie]):
    """A Cookies management class, built on top of biscuits."""

    def set(self, name, *args, **kwargs):
        self[name] = Cookie(name, *args, **kwargs)

    @staticmethod
    def from_environ(environ: dict):
        return parse(environ.get('HTTP_COOKIE', ''))


class Query(TypeCastingDict):

    @classmethod
    def from_value(cls, value: str):
        return cls(parse_qsl(
            value, keep_blank_values=True, strict_parsing=True))

    @classmethod
    def from_environ(cls, environ: dict):
        qs = environ.get('QUERY_STRING', '')
        if qs:
            return cls.from_value(qs)
        return cls()
