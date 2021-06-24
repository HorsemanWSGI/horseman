import pytest
import webtest
from unittest.mock import Mock
from http import HTTPStatus
import horseman.response



def test_can_set_status_from_numeric_value():
    response = horseman.response.Response.create(202)
    assert response.status == HTTPStatus.ACCEPTED


def test_raises_if_code_is_unknown():
    with pytest.raises(ValueError):
        horseman.response.Response.create(999)


def test_wrong_body_type():
    environ = {
        'PATH_INFO': '/'
    }
    response = horseman.response.Response.create(200, body=object())
    start_response = Mock()
    with pytest.raises(TypeError):
        list(response(environ, start_response))

    start_response.assert_called_with('200 OK', [])


def test_bytes_representation_bodyless():
    app = webtest.TestApp(
        horseman.response.Response.create(HTTPStatus.ACCEPTED)
    )
    response = app.get('/')
    assert response.status_int == 202
    assert response.body == b'Request accepted, processing continues off-line'
    assert list(response.headers.items()) == [('Content-Length', '47')]


def test_representation_with_body():
    app = webtest.TestApp(
        horseman.response.Response.create(HTTPStatus.OK, body="Super")
    )
    response = app.get('/')
    assert response.status_int == 200
    assert response.body == b'Super'
    assert list(response.headers.items()) == [('Content-Length', '5')]


def test_representation_bodyless_with_body():
    app = webtest.TestApp(
        horseman.response.Response.create(
            HTTPStatus.NO_CONTENT, body="Super")
    )
    response = app.get('/')
    assert response.status_int == 204
    assert response.body == b''
    assert list(response.headers.items()) == []


def test_304_no_content_type():
    app = webtest.TestApp(
        horseman.response.Response.create(HTTPStatus.NOT_MODIFIED)
    )
    response = app.get('/')
    assert response.status_int == 304
    assert response.body == b''
    assert list(response.headers.items()) == []


def test_1XX_no_content_type():
    app = webtest.TestApp(
        horseman.response.Response.create(HTTPStatus.CONTINUE)
    )
    response = app.get('/', status=100)
    assert response.status_int == 100
    assert response.body == b''
    assert list(response.headers.items()) == []


def test_json_response():
    structure = {
        'Horseman': 'headless',
        'python3.8': True,
        'version': 0.1
    }

    app = webtest.TestApp(
        horseman.response.Response.to_json(body=structure)
    )
    response = app.get('/')
    assert response.status_int == 200
    assert response.body == (
        b'{"Horseman":"headless","python3.8":true,"version":0.1}')
    assert list(response.headers.items()) == [
        ('Content-Type', 'application/json'),
        ('Content-Length', '54')
    ]

    app = webtest.TestApp(
        horseman.response.Response.to_json(
            body=structure, headers={'Custom-Header': 'Test'}))
    response = app.get('/')
    assert response.status_int == 200
    assert response.body == (
        b'{"Horseman":"headless","python3.8":true,"version":0.1}')
    assert list(response.headers.items()) == [
        ('Custom-Header', 'Test'),
        ('Content-Type', 'application/json'),
        ('Content-Length', '54')
    ]

    app = webtest.TestApp(
        horseman.response.Response.to_json(
            HTTPStatus.ACCEPTED, body=structure,
            headers={'Custom-Header': 'Test'})
    )
    response = app.get('/')
    assert response.status_int == 202
    assert response.body == (
        b'{"Horseman":"headless","python3.8":true,"version":0.1}')
    assert list(response.headers.items()) == [
        ('Custom-Header', 'Test'),
        ('Content-Type', 'application/json'),
        ('Content-Length', '54')
    ]

    app = webtest.TestApp(
        horseman.response.Response.to_json(
            HTTPStatus.ACCEPTED, body=structure,
            headers={'Content-Type': 'wrong/content'})
    )
    response = app.get('/')
    assert response.status_int == 202
    assert response.body == (
        b'{"Horseman":"headless","python3.8":true,"version":0.1}')
    assert list(response.headers.items()) == [
        ('Content-Type', 'application/json'),
        ('Content-Length', '54')
    ]

    app = webtest.TestApp(
        horseman.response.Response.to_json(
            HTTPStatus.ACCEPTED, body=structure,
            headers={})
    )
    response = app.get('/')
    assert response.status_int == 202
    assert response.body == (
        b'{"Horseman":"headless","python3.8":true,"version":0.1}')
    assert list(response.headers.items()) == [
        ('Content-Type', 'application/json'),
        ('Content-Length', '54')
    ]


def test_json_errors():
    with pytest.raises(TypeError):
        horseman.response.Response.to_json(body=object())


def test_redirect():
    response = horseman.response.Response.redirect('/test')
    assert response.headers == {'Location': '/test'}
    assert response.body is None
    assert response.status == 303
    assert webtest.TestApp(response).get('/').body == (
        b'Object moved -- see Method and URL list')

    response = horseman.response.Response.redirect('/test', code=301)
    assert response.headers == {'Location': '/test'}
    assert response.body is None
    assert response.status == 301
    assert webtest.TestApp(response).get('/').body == (
        b'Object moved permanently -- see URI list')


def test_invalid_redirect():
    with pytest.raises(ValueError) as exc:
        horseman.response.Response.redirect('/test', code=400)
    assert str(exc.value) == '400: unknown redirection code.'


def test_response_cookies():
    response = horseman.response.Response.create()
    assert response.cookies == {}

    response.cookies.set('test', "{'this': 'is json'}")
    assert 'test' in response.cookies
    assert list(webtest.TestApp(response).get('/').headers.items()) == [
        ('Set-Cookie', 'test="{\'this\': \'is json\'}"; Path=/'),
        ('Content-Length', '35')
    ]
