import pytest
from horseman.environ import WSGIEnvironWrapper
from horseman.datastructures import Query, Data, ContentType, Cookies
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
    assert environ.cookies == Cookies('')
    assert environ.content_type == ContentType('')
    assert environ.data == Data()
    assert environ.application_uri == 'http://localhost'
    assert environ.uri() == 'http://localhost/?key%3D1'
    assert environ.uri(include_query=False) == 'http://localhost/'


def test_environ_inheritance():
    request = Request.blank('/?key=1', method='GET')
    environ = WSGIEnvironWrapper(request.environ)
    with pytest.raises(TypeError):
        WSGIEnvironWrapper(environ)


def test_environ_immutability():
    request = Request.blank('/?key=1', method='GET')
    environ = WSGIEnvironWrapper(request.environ)
    assert environ.path == '/'
    with pytest.raises(AttributeError):
        environ.path = '/test'

    del environ.path
    environ._environ['PATH_INFO'] = '/test'
    assert environ.path == '/test'
