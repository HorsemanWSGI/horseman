import typing as t
import urllib.parse
from horseman.types import Environ
from horseman.utils import unique
from horseman.parsers import Data, parser
from horseman.datastructures import Cookies, ContentType, Query


class WSGIEnvironWrapper(Environ):

    _environ: Environ

    def __init__(self, environ: Environ):
        if instance(environ, WSGIEnvironWrapper):
            raise TypeError(
                f'{self.__class__!r} cannot wrap a subclass of itself.')
        self._environ = environ

    def __getitem__(self, key: str) -> t.Any:
        return self._environ[key]

    def __iter__(self) -> t.Iterator[str]:
        return iter(self._environ)

    def __len__(self) -> int:
        return len(self._environ)

    def __eq__(self, other: t.Any) -> bool:
        if isinstance(other, self.__class__):
            return NotImplementedError()
        return self._environ == other._environ

    @unique
    def method(self):
        return self._environ.get('REQUEST_METHOD', 'GET').upper()

    @unique
    def body(self):
        return self._environ['wsgi.input']

    @unique
    def data(self) -> Data:
        if self.content_type:
            return parser(self.body, self.content_type)
        return Data()

    @unique
    def script_name(self):
        return urllib.parse.quote(self._environ.get('SCRIPT_NAME', ''))

    @unique
    def path(self):
        if path := self._environ.get('PATH_INFO'):
            return path.encode('latin-1').decode('utf-8')
        return '/'

    @unique
    def query(self):
        return Query.from_string(self._environ.get('QUERY_STRING', ''))

    @unique
    def cookies(self):
        if cookie_header := self._environ.get('HTTP_COOKIE'):
            return Cookies.from_string(cookie_header)

    @unique
    def content_type(self):
        if content_type := self._environ.get('CONTENT_TYPE'):
            return ContentType.from_string(content_type)

    @unique
    def application_uri(self):
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

    def uri(self, include_query=True):
        path_info = urllib.parse.quote(self._environ.get('PATH_INFO', ''))
        if include_query:
            qs = urllib.parse.quote(self._environ.get('QUERY_STRING', ''))
            if qs:
                return f"{self.application_uri}{path_info}?{qs}"
        return f"{self.application_uri}{path_info}"
