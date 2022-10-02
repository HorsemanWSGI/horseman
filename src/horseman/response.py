import orjson
import typing as t
from http import HTTPStatus
from multidict import CIMultiDict
from horseman.datastructures import Cookies
from horseman.types import Environ, HTTPCode, StartResponse, WSGICallable


BODYLESS = frozenset((
    HTTPStatus.CONTINUE,
    HTTPStatus.SWITCHING_PROTOCOLS,
    HTTPStatus.PROCESSING,
    HTTPStatus.NO_CONTENT,
    HTTPStatus.NOT_MODIFIED
))

REDIRECT = frozenset((
    HTTPStatus.MULTIPLE_CHOICES,
    HTTPStatus.MOVED_PERMANENTLY,
    HTTPStatus.FOUND,
    HTTPStatus.SEE_OTHER,
    HTTPStatus.NOT_MODIFIED,
    HTTPStatus.USE_PROXY,
    HTTPStatus.TEMPORARY_REDIRECT,
    HTTPStatus.PERMANENT_REDIRECT
))


class Headers(CIMultiDict):

    __slots__ = ('_cookies',)

    cookies: Cookies

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cookies = None

    @property
    def cookies(self):
        if self._cookies is None:
            self._cookies = Cookies()
        return self._cookies

    def items(self) -> t.Iterable[t.Tuple[str, str]]:
        yield from super().items()
        if self._cookies:
            for cookie in self._cookies.values():
                yield 'Set-Cookie', str(cookie)

    def coalesced_items(self) -> t.Iterable[t.Tuple[str, str]]:
        """Coalescence of headers does NOT garanty order of headers.
        It garanties the order of the header values, though.
        """
        if self._cookies:
            cookies = (str(cookie) for cookie in self._cookies.values())
        else:
            cookies = None

        keys = frozenset(self.keys())
        for header in keys:
            values = self.getall(header)
            if header == 'Set-Cookie' and cookies:
                values = [*values, *cookies]
            yield header, ', '.join(values)
        if 'Set-Cookie' not in self and cookies:
            yield 'Set-Cookie', ', '.join(cookies)


Finisher = t.Callable[['Response'], None]


class Response(WSGICallable):

    __slots__ = ('status', 'body', 'headers', '_finishers')

    status: HTTPStatus
    body: t.Optional[t.Union[t.AnyStr, t.Iterator[bytes]]]
    headers: Headers
    _finishers: t.Optional[t.Deque[Finisher]]

    def __init__(self, status: HTTPCode = 200,
                 body: t.Optional[t.Iterable] = None,
                 headers: t.Optional[Headers] = None):
        self.status = HTTPStatus(status)
        self.body = body
        self.headers = Headers(headers or [])
        self._finishers = None

    @property
    def cookies(self):
        return self.headers.cookies

    def close(self):
        """Exhaust the list of finishers. No error is handled here.
        An exception will cause the closing operation to fail during
        the finishers iteration.
        """
        if self._finishers:
            while self._finishers:
                finisher = self._finishers.popleft()
                finisher(self)

    def add_finisher(self, task: Finisher):
        if self._finishers is None:
            self._finishers = t.Deque()
        self._finishers.append(task)

    def __iter__(self) -> t.Iterator[bytes]:
        if self.status not in BODYLESS:
            if self.body is None:
                yield self.status.description.encode()
            elif isinstance(self.body, bytes):
                yield self.body
            elif isinstance(self.body, str):
                yield self.body.encode()
            elif isinstance(self.body, t.Iterable):
                yield from self.body
            else:
                raise TypeError(
                    f'Body of type {type(self.body)!r} is not supported.'
                )

    def __call__(self, environ: Environ,
                 start_response: StartResponse) -> t.Iterable[bytes]:
        status = f'{self.status.value} {self.status.phrase}'
        start_response(status, list(self.headers.items()))
        return self

    @classmethod
    def redirect(cls, location, code: HTTPCode = 303,
                 body: t.Optional[t.Iterable] = None,
                 headers: t.Optional[Headers] = None) -> 'Response':
        if code not in REDIRECT:
            raise ValueError(f"{code}: unknown redirection code.")
        if not headers:
            headers = {'Location': location}
        else:
            headers['Location'] = location
        return cls(code, body, headers)

    @classmethod
    def from_file_iterator(cls, filename: str, body: t.Iterable[bytes],
                           headers: t.Optional[Headers] = None):
        if headers is None:
            headers = {
                "Content-Disposition": f"attachment;filename={filename}"}
        elif "Content-Disposition" not in headers:
            headers["Content-Disposition"] = (
                f"attachment;filename={filename}")
        return cls(200, body, headers)

    @classmethod
    def to_json(cls, code: HTTPCode = 200, body: t.Optional[t.Any] = None,
                headers: t.Optional[Headers] = None):
        data = orjson.dumps(body)
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        else:
            headers['Content-Type'] = 'application/json'
        return cls(code, data, headers)

    @classmethod
    def from_json(cls, code: HTTPCode = 200, body: t.AnyStr = '',
                  headers: t.Optional[Headers] = None):
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        else:
            headers['Content-Type'] = 'application/json'
        return cls(code, body, headers)

    @classmethod
    def html(cls, code: HTTPCode = 200, body: t.AnyStr = '',
             headers: t.Optional[Headers] = None):
        if headers is None:
            headers = {'Content-Type': 'text/html; charset=utf-8'}
        else:
            headers['Content-Type'] = 'text/html; charset=utf-8'
        return cls(code, body, headers)
