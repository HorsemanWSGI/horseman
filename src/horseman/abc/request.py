import urllib.parse
from typing import TypeVar, Generic, Any
from authsources.protocols import RequestProtocol as BaseRequestProtocol
from abc import ABC, abstractmethod
from collections.abc import Mapping
from kettu.headers import Query, Cookies, ContentType
from horseman.abc.response import ResponseProtocol
from horseman.utils import immutable_cached_property


E = TypeVar("E", bound=Mapping)
T = TypeVar('T')


class RequestProtocol(ABC, BaseRequestProtocol, Generic[E]):
    environ: E
    response_cls: type[ResponseProtocol]

    @property
    @abstractmethod
    def method(self) -> str: ...

    @property
    @abstractmethod
    def domain(self) -> str: ...

    @property
    @abstractmethod
    def root_path(self) -> str: ...

    @property
    @abstractmethod
    def path(self) -> str: ...

    @property
    @abstractmethod
    def querystring(self) -> str | bytes: ...

    @property
    @abstractmethod
    def cookies(self) -> Cookies: ...

    @property
    @abstractmethod
    def content_type(self) -> ContentType: ...

    @property
    @abstractmethod
    def host(self) -> tuple[str | None, int | None]:
        ...

    @property
    @abstractmethod
    def scheme(self) -> str: ...

    @immutable_cached_property
    def query(self) -> Query:
        return Query.from_string(self.querystring)

    @immutable_cached_property
    def application_uri(self) -> str:
        scheme = self.scheme
        server, port = self.host
        if not port:
            port = (scheme == 'https' and 443 or 80)

        if (self.scheme == "http" and port == 80) or (
            self.scheme == "https" and port == 443
        ):
            return f"{scheme}://{server}{self.root_path}"
        return f"{scheme}://{server}:{port}{self.root_path}"

    def uri(self, include_query: bool = True) -> str:
        path_info = urllib.parse.quote(self.path)
        if include_query:
            qs = urllib.parse.quote(self.querystring)
            if qs:
                return f"{self.application_uri}{path_info}?{qs}"
        return f"{self.application_uri}{path_info}"
