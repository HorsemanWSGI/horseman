import pytest
from horseman.request import Request
from kettu.headers import Query, ContentType, Cookies
from kettu.datastructures import Data
from webtest.app import TestRequest as WEBRequest


def test_environ():
    environ = WEBRequest.blank('/?key=1', method='GET').environ
    request = Request(environ)
    assert isinstance(request, Request)

    assert request.path == '/'
    assert request.method == 'GET'
    assert request.body.read() == b''
    assert request.query == Query({'key': ('1',)})
    assert request.root_path == ''
    assert request.cookies == None
    assert request.content_type == None
    assert request.data == Data()
    assert request.application_uri == 'http://localhost'
    assert request.uri() == 'http://localhost/?key%3D1'
    assert request.uri(include_query=False) == 'http://localhost/'


def test_environ_immutability():
    environ = WEBRequest.blank('/?key=1', method='GET').environ
    request = Request(environ)
    assert request.path == '/'
    with pytest.raises(AttributeError):
        request.path = '/test'

    del request.path
    request.environ['PATH_INFO'] = '/test'
    assert request.path == '/test'
