import pytest
import horseman.meta
import horseman.routing
import horseman.http
import horseman.response
import http
import autoroutes
import webtest


class MockOverhead(horseman.meta.Overhead):

    def __init__(self, node, environ, **params):
        self.node = node
        self.environ = environ
        self.params = params
        self.data = {}

    def set_data(self, data):
        self.data.update(data)


class MockRoutingNode(horseman.routing.RoutingNode):

    request_factory = MockOverhead

    def __init__(self):
        self.routes = autoroutes.Routes()


class MockSentryNode(MockRoutingNode, horseman.routing.SentryNode):


    def __init__(self, *args):
        super().__init__(*args)
        self.exceptions = []

    def handle_exception(self, exc_info, environ):
        self.exceptions.append(exc_info)


def fake_route(request):
    return horseman.response.Response.create(200, body=b'OK !')


def failing_route(request):
    raise RuntimeError('Oh, I failed !')


class TestRoutingNode:

    def setup_method(self, method):
        self.node = MockRoutingNode()
        self.node.route('/getter', methods=['GET'])(fake_route)
        self.node.route('/poster', methods=['POST'])(fake_route)

    def test_lookup(self):
        route, params = self.node.lookup('/getter', {})
        assert 'GET' in route
        assert route['GET'] == fake_route
        assert params == {}

        route, params = self.node.lookup('/poster', {})
        assert 'POST' in route
        assert route['POST'] == fake_route
        assert params == {}

    def test_process_endpoint(self):
        environ = {'REQUEST_METHOD': 'GET'}
        routing = self.node.lookup('/getter', {})
        result = self.node.process_endpoint(environ, routing)
        assert isinstance(result, horseman.response.Response)

        with pytest.raises(horseman.http.HTTPError) as exc:
            self.node.process_endpoint({'REQUEST_METHOD': 'POST'}, routing)

        # METHOD UNALLOWED.
        assert exc.value.status == http.HTTPStatus(405)

    def test_routing(self):
        environ = {
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/getter',
        }
        result = self.node.routing(environ)
        assert isinstance(result, horseman.response.Response)

        environ = {
            'REQUEST_METHOD': 'POST',
            'PATH_INFO': '/getter',
        }
        with pytest.raises(horseman.http.HTTPError) as exc:
            self.node.routing(environ)

        # METHOD UNALLOWED.
        assert exc.value.status == http.HTTPStatus(405)

    def test_wsgi_roundtrip(self):
        app = webtest.TestApp(self.node)

        response = app.get('/', status=404)
        assert response.body == b'Nothing matches the given URI'

        response = app.get('/getter')
        assert response.body == b'OK !'

        response = app.post('/getter', status=405)
        assert response.body == b'Specified method is invalid for this resource'


class TestSentryNode(TestRoutingNode):

    def setup_method(self, method):
        self.node = MockSentryNode()
        self.node.route('/getter', methods=['GET'])(fake_route)
        self.node.route('/poster', methods=['POST'])(fake_route)
        self.node.route('/failer', methods=['GET'])(failing_route)

    def test_sentry_exception_handling(self):
        app = webtest.TestApp(self.node)

        with pytest.raises(RuntimeError):
            app.get('/failer', status=500)

        assert len(self.node.exceptions) == 1
        cls, inst, tb = self.node.exceptions[0]
        assert cls is RuntimeError
