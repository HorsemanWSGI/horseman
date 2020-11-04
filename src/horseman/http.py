from http import HTTPStatus
from typing import TypeVar
from urllib.parse import parse_qs
from biscuits import Cookie, parse
from horseman.prototyping import HTTPCode


class HTTPError(Exception):

    def __init__(self, status: HTTPCode, body: str=None):
        self.status = HTTPStatus(status)
        self.body = body or self.status.description

    def __bytes__(self):
        return b'HTTP/1.1 %a %b\r\nContent-Length: %a\r\n\r\n%b' % (
            self.status.value, self.status.phrase.encode(),
            len(self.body), self.body)


class Multidict(dict):
    """Data structure to deal with several values for the same key.

    Useful for query string parameters or form-like POSTed ones.
    """

    def get(self, key: str, default=...):
        return self.getlist(key, [default])[0]

    def getlist(self, key: str, default=...):
        try:
            return self[key]
        except KeyError:
            if default is ... or default == [...]:
                raise HTTPError(HTTPStatus.BAD_REQUEST,
                                "Missing '{}' key".format(key))
            return default

    def dict_items(self):
        for key in self.keys():
            if key.endswith('[]'):
                yield key[:-2], self.getlist(key)
            else:
                yield key, self.get(key)

    def dict(self):
        return {k: v for k, v in self.dict_items()}


class TypeCastingDict(Multidict):

    TRUE_STRINGS = ('t', 'true', 'yes', '1', 'on')
    FALSE_STRINGS = ('f', 'false', 'no', '0', 'off')
    NONE_STRINGS = ('n', 'none', 'null')

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
        raise HTTPError(
            HTTPStatus.BAD_REQUEST,
            "Wrong boolean value for '{}={}'".format(key, self.get(key)))

    def int(self, key: str, default=...):
        try:
            return int(self.get(key, default))
        except ValueError:
            raise HTTPError(HTTPStatus.BAD_REQUEST,
                            "Key '{}' must be castable to int".format(key))

    def float(self, key: str, default=...):
        try:
            return float(self.get(key, default))
        except ValueError:
            raise HTTPError(HTTPStatus.BAD_REQUEST,
                            "Key '{}' must be castable to float".format(key))


class Query(TypeCastingDict):

    @classmethod
    def from_value(cls, value: str):
        return cls(parse_qs(
            value, keep_blank_values=True, strict_parsing=True))

    @classmethod
    def from_environ(cls, environ: dict):
        return cls.from_value(environ.get('QUERY_STRING', ''))


class Form(TypeCastingDict):
    pass


class Files(Multidict):
    """
    """


class Cookies(dict):
    """A Cookies management class, built on top of biscuits."""

    def set(self, name, *args, **kwargs):
        self[name] = Cookie(name, *args, **kwargs)

    @staticmethod
    def from_environ(environ: dict):
        return parse(environ.get('HTTP_COOKIE', ''))
