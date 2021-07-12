from horseman.meta import APIView, Overhead
from horseman.response import Response


class Request(Overhead):

    data = None

    def __init__(self, environ):
        self.environ = environ

    def extract(self):
        self.data = 'somedata'


def test_apiview():

    class View(APIView):

        def GET(self, overhead):
            return Response(200, b'You got it.')

    environ = {'REQUEST_METHOD': 'GET'}
    request = Request(environ)
    response = View()(request)
    assert response.body == b'You got it.'

    environ = {'REQUEST_METHOD': 'POST'}
    request = Request(environ)
    response = View()(request)
    assert response.status.value == 405
    assert next(iter(response)) == (
        b'Specified method is invalid for this resource'
    )


def test_api_view_multiple_methods():

    class View(APIView):

        def GET(self, overhead):
            return Response(body=b'You got it.')

        def POST(self, overhead):
            return Response(body=b'You posted it.')

    environ = {'REQUEST_METHOD': 'GET'}
    request = Request(environ)
    response = View()(request)
    assert response.body == b'You got it.'

    environ = {'REQUEST_METHOD': 'POST'}
    request = Request(environ)
    response = View()(request)
    assert response.status.value == 200
    assert response.body == b'You posted it.'
