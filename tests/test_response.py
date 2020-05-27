import pytest
import webtest
from http import HTTPStatus
import horseman.response


def test_can_set_status_from_numeric_value():
    response = horseman.response.Response.create(202)
    assert response.status == HTTPStatus.ACCEPTED


def test_raises_if_code_is_unknown():
    with pytest.raises(ValueError):
        horseman.response.Response.create(999)


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
    assert response.body ==  b'Super'
    assert list(response.headers.items()) == [('Content-Length', '5')]


def test_representation_bodyless_with_body():
    app = webtest.TestApp(
        horseman.response.Response.create(HTTPStatus.NO_CONTENT, body="Super")
    )
    response = app.get('/')
    assert response.status_int == 204
    assert response.body ==  b''
    assert list(response.headers.items()) == []


def test_304_no_content_type():
    app = webtest.TestApp(
        horseman.response.Response.create(HTTPStatus.NOT_MODIFIED)
    )
    response = app.get('/')
    assert response.status_int == 304
    assert response.body ==  b''
    assert list(response.headers.items()) == []


def test_1XX_no_content_type():
    app = webtest.TestApp(
        horseman.response.Response.create(HTTPStatus.CONTINUE)
    )
    response = app.get('/', status=100)
    assert response.status_int == 100
    assert response.body ==  b''
    assert list(response.headers.items()) == []


def test_json_response():
    structure = {
        'Horseman': 'headless',
        'python3.8': True,
        'version': 0.1
    }

    app = webtest.TestApp(
        horseman.response.json_reply(body=structure)
    )
    response = app.get('/')
    assert response.status_int == 200
    assert response.body ==  b'{"Horseman": "headless", "python3.8": true, "version": 0.1}'
    assert list(response.headers.items()) == [
        ('Content-Type', 'application/json'),
        ('Content-Length', '59')
    ]

    app = webtest.TestApp(
        horseman.response.json_reply(body=structure, headers={'Custom-Header': 'Test'})
    )
    response = app.get('/')
    assert response.status_int == 200
    assert response.body ==  b'{"Horseman": "headless", "python3.8": true, "version": 0.1}'
    assert list(response.headers.items()) == [
        ('Custom-Header', 'Test'),
        ('Content-Type', 'application/json'),
        ('Content-Length', '59')
    ]

    app = webtest.TestApp(
        horseman.response.json_reply(
            HTTPStatus.ACCEPTED, body=structure,
            headers={'Custom-Header': 'Test'})
    )
    response = app.get('/')
    assert response.status_int == 202
    assert response.body ==  b'{"Horseman": "headless", "python3.8": true, "version": 0.1}'
    assert list(response.headers.items()) == [
        ('Custom-Header', 'Test'),
        ('Content-Type', 'application/json'),
        ('Content-Length', '59')
    ]

    app = webtest.TestApp(
        horseman.response.json_reply(
            HTTPStatus.ACCEPTED, body=structure,
            headers={'Content-Type': 'wrong/content'})
    )
    response = app.get('/')
    assert response.status_int == 202
    assert response.body ==  b'{"Horseman": "headless", "python3.8": true, "version": 0.1}'
    assert list(response.headers.items()) == [
        ('Content-Type', 'application/json'),
        ('Content-Length', '59')
    ]

    app = webtest.TestApp(
        horseman.response.json_reply(
            HTTPStatus.ACCEPTED, body=structure,
            headers={})
    )
    response = app.get('/')
    assert response.status_int == 202
    assert response.body ==  b'{"Horseman": "headless", "python3.8": true, "version": 0.1}'
    assert list(response.headers.items()) == [
        ('Content-Type', 'application/json'),
        ('Content-Length', '59')
    ]


def test_json_errors():
    with pytest.raises(TypeError):
        horseman.response.json_reply(body=object())
