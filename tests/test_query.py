import pytest
from webtest.app import TestRequest as Request
from horseman.http import Query


def test_query():
    q = Query.from_environ({})
    assert isinstance(q, Query)
    assert len(q) == 0


def test_float_should_cast_to_float():
    request = Request.blank('/?key=1', method='GET')
    query = Query.from_environ(request.environ)
    assert query.float('key') == 1.0

    request = Request.blank('/?key=42.1', method='GET')
    query = Query.from_environ(request.environ)
    assert query.float('key') == 42.1

    request = Request.blank('/?key=-75', method='GET')
    query = Query.from_environ(request.environ)
    assert query.float('key') == -75

    request = Request.blank('/?key=-75.5', method='GET')
    query = Query.from_environ(request.environ)
    assert query.float('key') == -75.5

    request = Request.blank('/?key=-75,5', method='GET')
    query = Query.from_environ(request.environ)
    with pytest.raises(ValueError):
        query.int('key')

    request = Request.blank('/?key=dang!', method='GET')
    query = Query.from_environ(request.environ)
    with pytest.raises(ValueError):
        query.int('key')


def test_bool_should_cast_to_boolean():
    for value in Query.TRUE_STRINGS:
        request = Request.blank(f'/?key={value}', method='GET')
        query = Query.from_environ(request.environ)
        assert query.bool('key') is True

    for value in Query.FALSE_STRINGS:
        request = Request.blank(f'/?key={value}', method='GET')
        query = Query.from_environ(request.environ)
        assert query.bool('key') is False

    for value in Query.NONE_STRINGS:
        request = Request.blank(f'/?key={value}', method='GET')
        query = Query.from_environ(request.environ)
        assert query.bool('key') is None

    request = Request.blank('/?key=Z', method='GET')
    query = Query.from_environ(request.environ)
    with pytest.raises(ValueError) as exc:
        query.bool('key')
    assert str(exc.value) == "Can't cast 'z' to boolean."

    q = Query({'foo': True, 'bar': False, 'crux': None})
    assert q.bool('foo') is True
    assert q.bool('bar') is False
    assert q.bool('crux') is None


def test_int_should_cast_to_int():
    request = Request.blank('/?key=1', method='GET')
    query = Query.from_environ(request.environ)
    assert query.int('key') == 1

    request = Request.blank('/?key=42', method='GET')
    query = Query.from_environ(request.environ)
    assert query.int('key') == 42

    request = Request.blank('/?key=-75', method='GET')
    query = Query.from_environ(request.environ)
    assert query.int('key') == -75

    request = Request.blank('/?key=75.5', method='GET')
    query = Query.from_environ(request.environ)
    with pytest.raises(ValueError):
        query.int('key')

    request = Request.blank('/?key=dang!', method='GET')
    query = Query.from_environ(request.environ)
    with pytest.raises(ValueError):
        query.int('key')
