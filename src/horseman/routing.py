import sys
import inspect
from autoroutes import Routes
from http import HTTPStatus
from horseman.meta import Overhead, APINode, view_methods
from horseman.http import HTTPError


def route_payload(view, methods: list=None):
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
    return payload


def add_route(router, path: str, methods: list=None, **extras: dict):

    def route_from_view_or_function(view):
        payload = route_payload(view, methods)
        payload.update(extras)
        router.add(path, **payload)
        return view

    return route_from_view_or_function


class RoutingNode(APINode):

    routes: Routes
    request_factory: Overhead

    __slots__ = ('routes', 'request_factory')

    def route(self, path: str, methods: list=None, **extras: dict):
        return add_route(self.routes, path, methods, **extras)

    def process_endpoint(self, environ, routing_args):
        methods, params = routing_args  # unpacking the routing result
        endpoint = methods.get(environ['REQUEST_METHOD'])
        if endpoint is None:
            raise HTTPError(HTTPStatus.METHOD_NOT_ALLOWED)
        request = self.request_factory(self, environ, **params)
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
