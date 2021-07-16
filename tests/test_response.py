import pytest
import webtest
from unittest.mock import Mock
from http import HTTPStatus
from horseman.response import Response, file_iterator


def test_file_iterator(tmpdir):

    fpath = tmpdir / 'test.txt'
    with fpath.open('w+') as fd:
        fd.write('This is a sentence')

    fiter = file_iterator(fpath, chunk=3)
    chunks = list(fiter)
    assert chunks == [b'Thi', b's i', b's a', b' se', b'nte', b'nce']

    fiter = file_iterator(fpath)
    chunks = list(fiter)
    assert chunks == [b'This is a sentence']

    response = Response.from_file_iterator(
        'test.txt', file_iterator(fpath))
    assert response.status == 200
    assert list(response.headers.items()) == [
        ('Content-Disposition', 'attachment;filename=test.txt')
    ]
    assert list(response) == [b'This is a sentence']

    response = Response.from_file_iterator(
        'test.txt', file_iterator(fpath),
        headers={"Content-Type": "foo"}
    )
    assert list(response.headers.items()) == [
        ('Content-Type', 'foo'),
        ('Content-Disposition', 'attachment;filename=test.txt')
    ]

    response = Response.from_file_iterator(
        'test.txt', file_iterator(fpath),
        headers={"Content-Disposition": "foobar"}
    )
    assert list(response.headers.items()) == [
        ('Content-Disposition', 'foobar')
    ]


def test_can_set_status_from_numeric_value():
    response = Response(202)
    assert response.status == HTTPStatus.ACCEPTED


def test_raises_if_code_is_unknown():
    with pytest.raises(ValueError):
        Response(999)


def test_wrong_body_type():
    environ = {
        'PATH_INFO': '/'
    }
    response = Response(200, body=object())
    start_response = Mock()
    with pytest.raises(TypeError):
        list(response(environ, start_response))

    start_response.assert_called_with('200 OK', [])


def test_bytes_representation_bodyless():
    app = webtest.TestApp(
        Response(HTTPStatus.ACCEPTED)
    )
    response = app.get('/')
    assert response.status_int == 202
    assert response.body == (
        b'Request accepted, processing continues off-line'
    )
    assert list(response.headers.items()) == [('Content-Length', '47')]


def test_representation_with_body():
    app = webtest.TestApp(
        Response(HTTPStatus.OK, body="Super")
    )
    response = app.get('/')
    assert response.status_int == 200
    assert response.body == b'Super'
    assert list(response.headers.items()) == [('Content-Length', '5')]


def test_representation_bodyless_with_body():
    app = webtest.TestApp(
        Response(
            HTTPStatus.NO_CONTENT, body="Super")
    )
    response = app.get('/')
    assert response.status_int == 204
    assert response.body == b''
    assert list(response.headers.items()) == []


def test_304_no_content_type():
    app = webtest.TestApp(
        Response(HTTPStatus.NOT_MODIFIED)
    )
    response = app.get('/')
    assert response.status_int == 304
    assert response.body == b''
    assert list(response.headers.items()) == []


def test_1XX_no_content_type():
    app = webtest.TestApp(
        Response(HTTPStatus.CONTINUE)
    )
    response = app.get('/', status=100)
    assert response.status_int == 100
    assert response.body == b''
    assert list(response.headers.items()) == []


def test_json_response_headers():
    response = Response.from_json(body="{}")
    assert list(response.headers.items()) == [
        ('Content-Type', 'application/json')
    ]

    response = Response.from_json(
        body="{}", headers={"Content-Type": "text/html"})
    assert list(response.headers.items()) == [
        ('Content-Type', 'application/json')
    ]


def test_html_response():

    response = Response.html(body="<html></html>")
    assert list(response.headers.items()) == [
        ('Content-Type', 'text/html; charset=utf-8')
    ]

    response = Response.html(
        body="{}", headers={"Content-Type": "text/plain"})
    assert list(response.headers.items()) == [
        ('Content-Type', 'text/html; charset=utf-8')
    ]


def test_json_response():
    structure = {
        'Horseman': 'headless',
        'python3.8': True,
        'version': 0.1
    }

    app = webtest.TestApp(
        Response.to_json(body=structure)
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
        Response.to_json(
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
        Response.to_json(
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
        Response.to_json(
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
        Response.to_json(
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
        Response.to_json(body=object())


def test_redirect():
    response = Response.redirect('/test')
    assert list(response.headers.items()) == [('Location', '/test')]
    assert response.body is None
    assert response.status == 303
    assert webtest.TestApp(response).get('/').body == (
        b'Object moved -- see Method and URL list')

    response = Response.redirect('/test', code=301)
    assert list(response.headers.items()) == [('Location', '/test')]
    assert response.body is None
    assert response.status == 301
    assert webtest.TestApp(response).get('/').body == (
        b'Object moved permanently -- see URI list'
    )

    response = Response.redirect(
        '/test', code=301, headers={"Location": "/outside"})
    assert list(response.headers.items()) == [('Location', '/test')]
    assert response.body is None
    assert response.status == 301
    assert webtest.TestApp(response).get('/').body == (
        b'Object moved permanently -- see URI list'
    )


def test_invalid_redirect():
    with pytest.raises(ValueError) as exc:
        Response.redirect('/test', code=400)
    assert str(exc.value) == '400: unknown redirection code.'


def test_response_cookies():
    response = Response()
    assert response.cookies == {}
    assert response.cookies is response.headers.cookies


def test_finishers():
    from collections import deque

    response = Response()
    assert response._finishers is None
    assert response.close() is None

    task = Mock()
    response.add_finisher(task)
    assert response._finishers is not None
    assert isinstance(response._finishers, deque)
    assert len(response._finishers) == 1
    assert task.called is False

    response.close()
    assert task.called is True
    assert task.assert_called_with() is None


def test_finishers_order():
    calls = []

    def tasker(num):
        def task():
            calls.append(num)
        return task

    response = Response()
    response.add_finisher(tasker(1))
    response.add_finisher(tasker(2))
    response.add_finisher(tasker(3))
    response.close()

    assert calls == [1, 2, 3]

    response.add_finisher(tasker(3))
    response.add_finisher(tasker(2))
    response.add_finisher(tasker(1))
    response.close()
    assert calls == [1, 2, 3, 3, 2, 1]


def test_exception_finisher():

    calls = []

    def tasker(num):
        def task():
            if num == 2:
                raise RuntimeError('I do not want a 2')
            calls.append(num)
        return task

    response = Response()
    response.add_finisher(tasker(1))
    response.add_finisher(tasker(2))
    response.add_finisher(tasker(3))

    with pytest.raises(RuntimeError):
        response.close()

    assert calls == [1]
    assert len(response._finishers) == 1  # tasker(3) never popped.

    # We can resume by calling close again.
    # Note that the task responsible for the exception is lost at
    # thus point.
    response.close()
    assert calls == [1, 3]
    assert len(response._finishers) == 0
