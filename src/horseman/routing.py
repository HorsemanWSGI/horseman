import sys
import inspect
from autoroutes import Routes
from http import HTTPStatus
from horseman.meta import Overhead, APINode, view_methods
from horseman.http import HTTPError


class RoutingNode(APINode):

    request_type = None

    def __init__(self):
        self.routes = Routes()

    def route(self, path: str, methods: list=None, **extras: dict):

        def add_route(view):
            nonlocal methods
            if inspect.isclass(view):
                if methods is not None:
                    raise AttributeError(
                        "Can't use `methods` with class view")

                inst = view()
                payload = {
                    method: func for method, func in view_methods(inst)}
                if not payload:
                    raise ValueError(f"Empty view: {view}")
            else:
                if methods is None:
                    methods = ['GET']
                payload = {method: view for method in methods}

            payload.update(extras)
            self.routes.add(path, **payload)
            return view

        return add_route

    def process_endpoint(self, environ, routing_args):
        methods, params = routing_args  # unpacking the routing result
        endpoint = methods.get(environ['REQUEST_METHOD'])
        if endpoint is None:
            raise HTTPError(HTTPStatus.METHOD_NOT_ALLOWED)
        request = self.request_type(environ, **params)
        return endpoint(request)

    def lookup(self, path_info, environ):
         found = self.routes.match(path_info)
         if found == (None, None):
             return None
         return found


class SentryNode(APINode):

    def handle_exception(self, exc_info, environ):
        pass

    def __call__(self, environ, start_response):
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
