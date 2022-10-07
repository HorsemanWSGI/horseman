import typing as t
from http import HTTPStatus
from multidict import CIMultiDict
from horseman.datastructures import Cookies
from horseman.types import Environ, HTTPCode, StartResponse


BODYLESS = frozenset((
    HTTPStatus.CONTINUE,
    HTTPStatus.SWITCHING_PROTOCOLS,
    HTTPStatus.PROCESSING,
    HTTPStatus.NO_CONTENT,
    HTTPStatus.NOT_MODIFIED
))

BodyT = t.Union[str, bytes, t.Iterator[bytes]]
HeadersT = t.Union[t.Mapping[str, str], t.Iterable[t.Tuple[str, str]]]


class Headers(CIMultiDict[str]):

    __slots__ = ('_cookies',)

    _cookies: Cookies

    def __new__(cls, *args, **kwargs):
        if not kwargs and len(args) == 1 and isinstance(args[0], cls):
            return args[0]
        inst = super().__new__(cls, *args, **kwargs)
        inst._cookies = None
        return inst

    @property
    def cookies(self) -> Cookies:
        if self._cookies is None:
            self._cookies = Cookies()
        return self._cookies

    def items(self):
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


class Response:

    __slots__ = ('status', 'body', 'headers', '_finishers')

    status: HTTPStatus
    body: t.Optional[BodyT]
    headers: Headers
    _finishers: t.Optional[t.Deque[Finisher]]

    def __init__(self,
                 status: HTTPCode = 200,
                 body: BodyT = None,
                 headers: t.Optional[HeadersT] = None):
        self.status = HTTPStatus(status)
        self.body = body
        self.headers = Headers(headers or ())  # idempotent.
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
