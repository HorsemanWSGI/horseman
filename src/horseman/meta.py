import sys
from abc import ABC, abstractmethod
from typing import TypeVar
from horseman.response import Response
from horseman.http import HTTPError
from horseman.types import (
    WSGICallable, Environ, StartResponse, ExceptionInfo)


Data = TypeVar('Data')


class Overhead(ABC):
    """WSGI Environ Overhead aka Request representation
    This object contains everything needed to handle a request.
    It can carry DB connectors, parsed data and other utils.
    """
    data: Data
    environ: Environ

    @abstractmethod
    def extract(self) -> Data:
        """Extracts the data from the incoming HTTP request.
        """


class APIView:
    """View with methods to act as HTTP METHOD dispatcher.
    Method names of the class must be a valid uppercase HTTP METHOD name.
    example : OPTIONS, GET, POST
    """

    def __call__(self, overhead: Overhead) -> Response:
        method = overhead.environ['REQUEST_METHOD'].upper()
        if worker := getattr(self, method, None):
            return worker(overhead)

        # Method not allowed
        return Response(405)


class Node(WSGICallable):

    @abstractmethod
    def resolve(self, path_info: str, environ: Environ) -> WSGICallable:
        """Resolves the path into a wsgi callable (eg. Response).
        If nothing was found, returns None or a WSGI callable corresponding
        to the HTTP Error (404, 405, 406).
        """

    def __call__(self, environ: Environ, start_response: StartResponse):
        # according to PEP 3333 the native string representing PATH_INFO
        # (and others) can only contain unicode codepoints from 0 to 255,
        # which is why we need to decode to latin-1 instead of utf-8 here.
        # We transform it back to UTF-8
        path_info = environ['PATH_INFO'].encode('latin-1').decode('utf-8')
        try:
            response = self.resolve(path_info, environ)
            if response is None:
                response = Response(404)

        except HTTPError as error:
            # FIXME: Log.
            response = Response(error.status, error.body)
        return response(environ, start_response)


class SentryNode(Node):

    @abstractmethod
    def handle_exception(self, exc_info: ExceptionInfo, environ: Environ):
        """This method handles exceptions happening while the
        application is trying to render/process/interpret the request.
        """

    def __call__(self, environ: Environ, start_response: StartResponse):
        iterable = None
        try:
            iterable = super().__call__(environ, start_response)
            yield from iterable
        except Exception:
            exc_info = sys.exc_info()
            self.handle_exception(exc_info, environ)
            exc_info = None
            raise
        finally:
            if hasattr(iterable, 'close'):
                try:
                    iterable.close()
                except Exception:
                    exc_info = sys.exc_info()
                    self.handle_exception(exc_info, environ)
                    exc_info = None
                    raise
