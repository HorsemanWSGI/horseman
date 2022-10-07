import pytest
import webtest
from unittest.mock import Mock
from http import HTTPStatus
from horseman.response import Response


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
    assert task.assert_called_with(response) is None


def test_finishers_order():
    calls = []

    def tasker(num):
        def task(response):
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
        def task(response):
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
