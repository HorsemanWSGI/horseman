# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from horseman.responder import reply


class BaseOverhead(ABC):

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

    def __call__(self, environ, overhead):
        method = environ['REQUEST_METHOD'].upper()
        worker = getattr(self, method, None)
        if worker is None:
            # Method not allowed
            response = reply(405)
        else:
            response = worker(environ, overhead)
        return response


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
        if routing_args:
            return self.process_endpoint(environ, routing_args)
        return None

    def __call__(self, environ, start_response):
        response = self.routing(environ)
        if response is None:
            response = reply(
                404, "Not found. Please consult the API documentation.")
        return response(environ, start_response)
