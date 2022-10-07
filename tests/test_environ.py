from horseman.environ import WSGIEnvironWrapper
from horseman.datastructures import Query, Data
from webtest.app import TestRequest as Request


def test_environ():
    request = Request.blank('/?key=1', method='GET')
    environ = WSGIEnvironWrapper(request.environ)
    assert isinstance(environ, WSGIEnvironWrapper)

    assert environ.path == '/'
    assert environ.method == 'GET'
    assert environ.body.read() == b''
    assert environ.query == Query({'key': ('1',)})
    assert environ.script_name == ''
    assert environ.cookies is None
    assert environ.content_type is None
    assert environ.data == Data()
    assert environ.application_uri == 'http://localhost'
    assert environ.uri() == 'http://localhost/?key%3D1'
    assert environ.uri(include_query=False) == 'http://localhost/'
