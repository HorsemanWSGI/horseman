from abc import ABC, abstractmethod
from inspect import isclass, isfunction, ismethod, getmembers

from horseman.definitions import METHODS
from horseman.response import Response
from horseman.http import HTTPError
from horseman.prototyping import Environ


class Overhead(ABC):
    """WSGI Environ Overhead aka Request representation
    This object contains everything needed to handle a request.
    It can carry DB connectors, parsed data and other utils.
    """

    environ: Environ = None

    @abstractmethod
    def __init__(self, node, environ: Environ, **params):
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
    The method names of the class must be a valid uppercase HTTP METHOD name
    example : OPTIONS, GET, POST
    """

    def __call__(self, overhead, environ):
        method = environ['REQUEST_METHOD'].upper()
        worker = getattr(self, method, None)
        if worker is not None:
            return worker(overhead, environ)

        # Method not allowed
        return Response.create(405)


def view_methods(vw):
    if isclass(vw):
        if issubclass(vw, APIView):
            predicate = lambda x: isfunction(x) and  x.__name__ in METHODS
        elif issubclass(vw, View):
            predicate = lambda x: (
                isfunction(x) and not x.__name__.startswith('_'))
        else:
            raise NotImplementedError(
                f'{vw} must be a subclass of `horseman.meta.View`')
    else:
        if isinstance(vw, APIView):
            predicate = lambda x: ismethod(x) and  x.__name__ in METHODS
        elif isinstance(vw, View):
            predicate = lambda x: (
                ismethod(x) and not x.__name__.startswith('_'))
        else:
            raise NotImplementedError(
                f'{vw} must be an instance of `horseman.meta.View`')

    return getmembers(vw, predicate=predicate)


class APINode(ABC):

    @abstractmethod
    def process_endpoint(self, environ, routing_args):
        """Process the looked up endpoint and returns a WSGI callable.
        """

    @abstractmethod
    def lookup(self, path_info, environ):
        """Lookups up the endpoint and returns the routing args, usually
        containing the possible conditional parameters and the controller.
        If nothing was found, returns None or a WSGI callable corresponding
        to the HTTP Error (404, 405, 406).
        """

    def routing(self, environ):
        # according to PEP 3333 the native string representing PATH_INFO
        # (and others) can only contain unicode codepoints from 0 to 255,
        # which is why we need to decode to latin-1 instead of utf-8 here.
        # We transform it back to UTF-8
        path_info = environ['PATH_INFO'].encode('latin-1').decode('utf-8')
        routing_args = self.lookup(path_info, environ)
        if routing_args is None:
            return None
        return self.process_endpoint(environ, routing_args)

    def __call__(self, environ, start_response):
        try:
            response = self.routing(environ)
            if response is None:
                response = Response.create(404)

        except HTTPError as error:
            # FIXME: Log.
            response = Response.create(error.status, error.message)
        return response(environ, start_response)
