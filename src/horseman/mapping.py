import re
import sys
import logging
from abc import ABC, abstractmethod
from typing import Mapping
from collections import UserDict
from horseman.exceptions import HTTPError
from horseman.response import Response
from horseman.types import (
    WSGICallable, Environ, StartResponse, ExceptionInfo)


slashes_normalization = re.compile(r"/+")


class Node(ABC):

    @abstractmethod
    def resolve(self, path_info: str, environ: Environ) -> WSGICallable:
        pass


class RootNode(Node, WSGICallable):

    def handle_exception(self, exc_info: ExceptionInfo, environ: Environ):
        """This method handles exceptions happening while the
        application is trying to render/process/interpret the request.
        """
        exctype, exc, traceback = exc_info
        if isinstance(exc, HTTPError):
            return Response(exc.status, body=exc.body)

    def __call__(self, environ: Environ, start_response: StartResponse):
        # according to PEP 3333 the native string representing PATH_INFO
        # (and others) can only contain unicode codepoints from 0 to 255,
        # which is why we need to decode to latin-1 instead of utf-8 here.
        # We transform it back to UTF-8
        # Note that it's valid for WSGI server to omit the value if it's
        # empty.
        path_info = environ.get(
            'PATH_INFO', '').encode('latin-1').decode('utf-8')
        if path_info:
            # Normalize the slashes to avoid things like '//test'
            path_info = slashes_normalization.sub("/", path_info)
        iterable = None
        try:
            iterable = self.resolve(path_info, environ)
            yield from iterable(environ, start_response)
        except Exception:
            iterable = self.handle_exception(sys.exc_info(), environ)
            if iterable is None:
                raise
            yield from iterable(environ, start_response)
        finally:
            if iterable is not None and hasattr(iterable, 'close'):
                try:
                    iterable.close()
                except Exception:
                    self.handle_exception(sys.exc_info(), environ)
                    raise


class Mapping(RootNode, UserDict, Mapping[str, WSGICallable]):

    NORMALIZE = re.compile('//+')

    @classmethod
    def normalize(cls, path: str):
        if not isinstance(path, str):
            raise ValueError(f'{cls} accepts only str keys.')
        if not path.startswith('/'):
            raise ValueError(f"Path must start with '/', got {path!r}")
        return cls.NORMALIZE.sub('/', path)

    def __setitem__(self, path: str, script: WSGICallable):
        super().__setitem__(self.normalize(path), script)

    def resolve(self, path_info: str, environ: Environ) -> WSGICallable:
        for script_name in sorted(self.keys(), key=len, reverse=True):
            if path_info.startswith(script_name):
                script = self[script_name]
                name = script_name.rstrip('/')
                environ['SCRIPT_NAME'] += name
                environ['PATH_INFO'] = path_info[len(name):]
                return script
        raise HTTPError(404)
