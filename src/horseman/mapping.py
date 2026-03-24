import sys
import typing as t
from pathlib import PurePosixPath
from abc import ABC, abstractmethod
from collections import UserDict
from horseman.exceptions import HTTPError
from horseman.response import Response
from horseman.types import (
    WSGICallable, Environ, StartResponse, ExceptionInfo)


class Node(ABC):

    @abstractmethod
    def resolve(self, environ: Environ) -> WSGICallable:
        pass


class RootNode(Node):

    def handle_exception(self, exc_info: ExceptionInfo, environ: Environ):
        """This method handles exceptions happening while the
        application is trying to render/process/interpret the request.
        """
        exctype, exc, traceback = exc_info
        if isinstance(exc, HTTPError):
            return Response(exc.status, body=exc.body)

    def __call__(self, environ: Environ, start_response: StartResponse):
        iterable = None
        try:
            iterable = self.resolve(environ)
            yield from iterable(environ, start_response)
        except Exception:
            iterable = self.handle_exception(sys.exc_info(), environ)
            if iterable is None:
                raise
            yield from iterable(environ, start_response)
        finally:
            if iterable is not None:
                closer: t.Optional[t.Callable[[], None]] = getattr(
                    iterable, 'close', None
                )
                if closer is not None:
                    try:
                        closer()
                    except Exception:
                        self.handle_exception(sys.exc_info(), environ)
                        raise


class Mapping(RootNode, UserDict, t.Mapping[str, WSGICallable]):

    def __setitem__(self, path: str, script: WSGICallable):
        super().__setitem__(str('/' / PurePosixPath(path)), script)

    def resolve(self, environ: Environ) -> WSGICallable:
        uri = PurePosixPath(environ.get('PATH_INFO', '/'))
        for current in (uri, *uri.parents):
            if (script := self.get(str(current))) is not None:
                if current.parents:
                    environ['SCRIPT_NAME'] += str(current)
                if current != uri:
                    environ['PATH_INFO'] = f'/{uri.relative_to(current)}'
                else:
                    environ['PATH_INFO'] = '/'
                return script
        raise HTTPError(404)
