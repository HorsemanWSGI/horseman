from http import HTTPStatus
from typing import TypeVar
from biscuits import Cookie


HTTPCode = TypeVar('HTTPCode', HTTPStatus, int)


class HTTPError(Exception):

    __slots__ = ('status', 'message')

    def __init__(self, http_code: HTTPCode, message: str=None):
        self.status = HTTPStatus(http_code)
        self.message = message or self.status.description

    def __bytes__(self):
        return b'HTTP/1.1 %a %b\r\nContent-Length: %a\r\n\r\n%b' % (
            self.status.value, self.status.phrase.encode(),
            len(self.message), self.message)


class Multidict(dict):
    """Data structure to deal with several values for the same key.

    Useful for query string parameters or form-like POSTed ones.
    """

    def get(self, key: str, default=...):
        return self.list(key, [default])[0]

    def list(self, key: str, default=...):
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
                yield key[:-2], self.list(key)
            else:
                yield key, self.get(key)

    def to_dict(self):
        return {k: v for k, v in self.dict_items()}


class Query(Multidict):

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


class Form(Query):
    """
    """


class Files(Multidict):
    """
    """


class Cookies(dict):
    """A Cookies management class, built on top of biscuits."""

    def set(self, name, *args, **kwargs):
        self[name] = Cookie(name, *args, **kwargs)
