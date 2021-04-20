import pytest
from webtest.app import TestRequest as Request
from horseman.http import Query, HTTPError


def test_float_should_cast_to_float():
    request = Request.blank(f'/?key=1', method='GET')
    query = Query.from_environ(request.environ)
    assert query.float('key') == 1.0

    request = Request.blank(f'/?key=42.1', method='GET')
    query = Query.from_environ(request.environ)
    assert query.float('key') == 42.1

    request = Request.blank(f'/?key=-75', method='GET')
    query = Query.from_environ(request.environ)
    assert query.float('key') == -75

    request = Request.blank(f'/?key=-75.5', method='GET')
    query = Query.from_environ(request.environ)
    assert query.float('key') == -75.5

    request = Request.blank(f'/?key=-75,5', method='GET')
    query = Query.from_environ(request.environ)
    with pytest.raises(HTTPError):
        query.int('key')

    request = Request.blank(f'/?key=dang!', method='GET')
    query = Query.from_environ(request.environ)
    with pytest.raises(HTTPError):
        query.int('key')


def test_bool_should_cast_to_boolean():
    for value in Query.TRUE_STRINGS:
        request = Request.blank(f'/?key={value}', method='GET')
        query = Query.from_environ(request.environ)
        assert query.bool('key') == True

    for value in Query.FALSE_STRINGS:
        request = Request.blank(f'/?key={value}', method='GET')
        query = Query.from_environ(request.environ)
        assert query.bool('key') == False

    for value in Query.NONE_STRINGS:
        request = Request.blank(f'/?key={value}', method='GET')
        query = Query.from_environ(request.environ)
        assert query.bool('key') is None

    request = Request.blank(f'/?key=Z', method='GET')
    query = Query.from_environ(request.environ)
    with pytest.raises(HTTPError):
        query.bool('key')


def test_int_should_cast_to_int():
    request = Request.blank(f'/?key=1', method='GET')
    query = Query.from_environ(request.environ)
    assert query.int('key') == 1

    request = Request.blank(f'/?key=42', method='GET')
    query = Query.from_environ(request.environ)
    assert query.int('key') == 42

    request = Request.blank(f'/?key=-75', method='GET')
    query = Query.from_environ(request.environ)
    assert query.int('key') == -75

    request = Request.blank(f'/?key=75.5', method='GET')
    query = Query.from_environ(request.environ)
    with pytest.raises(HTTPError):
        query.int('key')

    request = Request.blank(f'/?key=dang!', method='GET')
    query = Query.from_environ(request.environ)
    with pytest.raises(HTTPError):
        query.int('key')
