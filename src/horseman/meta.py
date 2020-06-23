import sys
from abc import ABC, abstractmethod
from typing import Dict

from horseman.response import Response
from horseman.http import HTTPError
from horseman.prototyping import (
    WSGICallable, Environ, StartResponse, ExceptionInfo)


class Node(WSGICallable):

    @abstractmethod
    def __call__(self,
                 environ: Environ,
                 start_response: StartResponse):
        """Abstract class to represent an application node.
        """


class Overhead(ABC):
    """WSGI Environ Overhead aka Request representation
    This object contains everything needed to handle a request.
    It can carry DB connectors, parsed data and other utils.
    """
    environ: Environ

    @abstractmethod
    def __init__(self, node: Node, environ: Environ, **params):
        pass

    @abstractmethod
    def set_data(self, data):
        """Set the data coming from the processing of the action.
        """


class View(ABC):
    pass


class APIView(View):
    """Implementation of an action as a class.
    This works as an HTTP METHOD dispatcher.
    Method names of the class must be a valid uppercase HTTP METHOD name.
    example : OPTIONS, GET, POST
    """

    def __call__(self, overhead: Overhead, environ: Environ) -> Response:
        method = environ['REQUEST_METHOD'].upper()
        if worker := getattr(self, method, None):
            return worker(overhead, environ)

        # Method not allowed
        return Response.create(405)



class APINode(Node):

    @abstractmethod
    def process_endpoint(self, endpoint, environ: Environ, **payload):
        """Process the looked up endpoint and returns a WSGI callable.
        """

    @abstractmethod
    def resolve(self, path_info: str, environ: Environ):
        """Lookups up the endpoint and returns the routing args, usually
        containing the possible conditional parameters and the controller.
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
                response = Response.create(404)

        except HTTPError as error:
            # FIXME: Log.
            response = Response.create(error.status, error.message)
        return response(environ, start_response)


class SentryNode(APINode):

    @abstractmethod
    def handle_exception(self, exc_info: ExceptionInfo, environ: Environ):
        """This method handles exceptions happening while the
        application is trying to render/process/interpret the request.
        """

    def __call__(self, environ: Environ, start_response: StartResponse):
        iterable = None

        try:
            iterable = super().__call__(environ, start_response)
            for event in iterable:
                yield event

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
