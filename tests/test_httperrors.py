import pytest
from http import HTTPStatus
from horseman.http import HTTPError


def test_exception():
    with pytest.raises(ValueError) as exc:
        HTTPError('abc')
    assert str(exc.value) == "'abc' is not a valid HTTPStatus"

    exc = HTTPError(400)
    assert exc.status == HTTPStatus(400)
    assert exc.body == 'Bad request syntax or unsupported method'

    exc = HTTPError(400, body='')
    assert exc.status == HTTPStatus(400)
    assert exc.body == ''
    assert bytes(exc) == (
        b'HTTP/1.1 400 Bad Request\r\n'
        b'Content-Length: 0\r\n\r\n'
    )

    exc = HTTPError(404, body='I did not find anything')
    assert exc.status == HTTPStatus(404)
    assert exc.body == 'I did not find anything'
    assert bytes(exc) == (
        b'HTTP/1.1 404 Not Found\r\n'
        b'Content-Length: 23\r\n\r\nI did not find anything'
    )

    exc = HTTPError(404, body=b'Works with bytes body')
    assert exc.status == HTTPStatus(404)
    assert exc.body == 'Works with bytes body'
    assert bytes(exc) == (
        b'HTTP/1.1 404 Not Found\r\n'
        b'Content-Length: 21\r\n\r\nWorks with bytes body'
    )

    with pytest.raises(ValueError) as exc:
        HTTPError(200, 200)
    assert str(exc.value) == "Body must be string or bytes."
