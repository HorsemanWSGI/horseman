import cgi
from http import HTTPStatus
from typing import NamedTuple, Dict, AnyStr
from urllib.parse import parse_qsl
from biscuits import Cookie, parse
from multidict import MultiDict
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


class TypeCastingDict(MultiDict):
    TRUE_STRINGS = {'t', 'true', 'yes', '1', 'on'}
    FALSE_STRINGS = {'f', 'false', 'no', '0', 'off'}
    NONE_STRINGS = {'n', 'none', 'null'}

    def bool(self, key: str, default=...):
        value = self.get(key, default)
        if value in (True, False, None):
            return value
        value = value.lower()
        if value in self.TRUE_STRINGS:
            return True
        elif value in self.FALSE_STRINGS:
            return False
        elif value in self.NONE_STRINGS:
            return None
        raise ValueError(f"Can't cast {value!r} to boolean.")

    def int(self, key: str, default=...):
        return int(self.get(key, default))

    def float(self, key: str, default=...):
        return float(self.get(key, default))


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


class Cookies(Dict[str, Cookie]):
    """A Cookies management class, built on top of biscuits."""

    def set(self, name, *args, **kwargs):
        self[name] = Cookie(name, *args, **kwargs)

    @staticmethod
    def from_environ(environ: dict):
        return parse(environ.get('HTTP_COOKIE', ''))
