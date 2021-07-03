import cgi
from http import HTTPStatus
from typing import NamedTuple, Dict
from urllib.parse import parse_qsl
from biscuits import Cookie, parse
from multidict import MultiDict
from horseman.types import HTTPCode, MIMEType


class HTTPError(Exception):

    def __init__(self, status: HTTPCode, body: str = None):
        self.status = HTTPStatus(status)
        self.body = body or self.status.description

    def __bytes__(self):
        return b'HTTP/1.1 %a %b\r\nContent-Length: %a\r\n\r\n%b' % (
            self.status.value, self.status.phrase.encode(),
            len(self.body), self.body)


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
