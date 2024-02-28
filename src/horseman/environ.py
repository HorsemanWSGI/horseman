import typing as t
import urllib.parse
from collections.abc import Mapping
from functools import cached_property
from horseman.types import Environ
from horseman.parsers import Data, parser
from horseman.datastructures import Cookies, ContentType, Query


class immutable_cached_property(cached_property):

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")

    def __delete__(self, instance):
        del instance.__dict__[self.attrname]


class WSGIEnvironWrapper(Environ):

    def __init__(self, environ: Environ):
        if isinstance(environ, WSGIEnvironWrapper):
            raise TypeError(
                f'{self.__class__!r} cannot wrap a subclass of itself.')
        self._environ: Environ = environ

    def __setitem__(self, key: str, value: t.Any):
        raise NotImplementedError(f'{self!r} is immutable')

    def __delitem__(self, key: str):
        raise NotImplementedError(f'{self!r} is immutable')

    def __getitem__(self, key: str) -> t.Any:
        return self._environ[key]

    def __iter__(self) -> t.Iterator[str]:
        return iter(self._environ)

    def __len__(self) -> int:
        return len(self._environ)

    def __eq__(self, other: t.Any) -> bool:
        if isinstance(other, self.__class__):
            return self._environ == other._environ
        if isinstance(other, Mapping):
            return self._environ == other
        raise NotImplementedError(
            f'{other!r} cannot be compared to {self!r}')

    @immutable_cached_property
    def method(self) -> str:
        return self._environ.get('REQUEST_METHOD', 'GET').upper()

    @immutable_cached_property
    def params(self) -> t.Dict[str, t.Any]:
        """Path params collected by the traversing or routing.
        """
        return self.get("PATH_PARAMS", {})

    @immutable_cached_property
    def body(self) -> t.BinaryIO:
        return self._environ['wsgi.input']

    @immutable_cached_property
    def data(self) -> Data:
        if self.content_type:
            return parser.parse(
                self._environ['wsgi.input'], self.content_type)
        return Data()

    @immutable_cached_property
    def domain(self) -> str:
        return self._environ['HTTP_HOST'].split(':', 1)[0]

    @immutable_cached_property
    def script_name(self) -> str:
        return urllib.parse.quote(self._environ.get('SCRIPT_NAME', ''))

    @immutable_cached_property
    def path(self) -> str:
        if path := self._environ.get('PATH_INFO'):
            return path.encode('latin-1').decode('utf-8')
        return '/'

    @immutable_cached_property
    def query(self) -> Query:
        return Query.from_string(self._environ.get('QUERY_STRING', ''))

    @immutable_cached_property
    def cookies(self) -> Cookies:
        return Cookies.from_string(self._environ.get('HTTP_COOKIE', ''))

    @immutable_cached_property
    def content_type(self) -> ContentType:
        return ContentType(self._environ.get('CONTENT_TYPE', ''))

    @immutable_cached_property
    def application_uri(self) -> str:
        scheme = self._environ.get('wsgi.url_scheme', 'http')
        http_host = self._environ.get('HTTP_HOST')
        if not http_host:
            server = self._environ['SERVER_NAME']
            port = self._environ.get('SERVER_PORT', '80')
        elif ':' in http_host:
            server, port = http_host.split(':', 1)
        else:
            server = http_host
            port = '80'

        if (scheme == 'http' and port == '80') or \
           (scheme == 'https' and port == '443'):
            return f'{scheme}://{server}{self.script_name}'
        return f'{scheme}://{server}:{port}{self.script_name}'

    def uri(self, include_query: bool = True) -> str:
        path_info = urllib.parse.quote(self._environ.get('PATH_INFO', ''))
        if include_query:
            qs = urllib.parse.quote(self._environ.get('QUERY_STRING', ''))
            if qs:
                return f"{self.application_uri}{path_info}?{qs}"
        return f"{self.application_uri}{path_info}"
