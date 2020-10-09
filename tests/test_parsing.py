import pytest


def test_bool_should_cast_to_boolean():
    from webtest.app import TestRequest
    from horseman.http import Query, HTTPError

    for value in Query.TRUE_STRINGS:
        request = TestRequest.blank(f'/?key={value}', method='GET')
        query = Query.from_environ(request.environ)
        assert query.bool('key') == True

    for value in Query.FALSE_STRINGS:
        request = TestRequest.blank(f'/?key={value}', method='GET')
        query = Query.from_environ(request.environ)
        assert query.bool('key') == False

    for value in Query.NONE_STRINGS:
        request = TestRequest.blank(f'/?key={value}', method='GET')
        query = Query.from_environ(request.environ)
        assert query.bool('key') is None

    request = TestRequest.blank(f'/?key=Z', method='GET')
    query = Query.from_environ(request.environ)
    with pytest.raises(HTTPError):
        query.bool('key')


def test_int_should_cast_to_int():
    from webtest.app import TestRequest
    from horseman.http import Query, HTTPError

    request = TestRequest.blank(f'/?key=1', method='GET')
    query = Query.from_environ(request.environ)
    assert query.int('key') == 1

    request = TestRequest.blank(f'/?key=42', method='GET')
    query = Query.from_environ(request.environ)
    assert query.int('key') == 42

    request = TestRequest.blank(f'/?key=-75', method='GET')
    query = Query.from_environ(request.environ)
    assert query.int('key') == -75

    request = TestRequest.blank(f'/?key=75.5', method='GET')
    query = Query.from_environ(request.environ)
    with pytest.raises(HTTPError):
        query.int('key')

    request = TestRequest.blank(f'/?key=dang!', method='GET')
    query = Query.from_environ(request.environ)
    with pytest.raises(HTTPError):
        query.int('key')


def test_float_should_cast_to_float():
    from webtest.app import TestRequest
    from horseman.http import Query, HTTPError

    request = TestRequest.blank(f'/?key=1', method='GET')
    query = Query.from_environ(request.environ)
    assert query.float('key') == 1.0

    request = TestRequest.blank(f'/?key=42.1', method='GET')
    query = Query.from_environ(request.environ)
    assert query.float('key') == 42.1

    request = TestRequest.blank(f'/?key=-75', method='GET')
    query = Query.from_environ(request.environ)
    assert query.float('key') == -75

    request = TestRequest.blank(f'/?key=-75.5', method='GET')
    query = Query.from_environ(request.environ)
    assert query.float('key') == -75.5

    request = TestRequest.blank(f'/?key=-75,5', method='GET')
    query = Query.from_environ(request.environ)
    with pytest.raises(HTTPError):
        query.int('key')

    request = TestRequest.blank(f'/?key=dang!', method='GET')
    query = Query.from_environ(request.environ)
    with pytest.raises(HTTPError):
        query.int('key')


def test_multipart():
    from io import BytesIO
    from webtest.app import TestApp
    from horseman.parsing import parse

    app = TestApp(None)
    content_type, body = app.encode_multipart(
        [('test', b'some value')],
        [('files[]', "baz-\xe9.png", b'abcdef', 'image/png'),
         ('files[]', "MyText.txt", b'ghi', 'text/plain')])

    form, files = parse(BytesIO(body), content_type)
    assert len(files['files[]']) == 2
    assert files['files[]'][0].filename == 'baz-é.png'
    assert files['files[]'][0].content_type == b'image/png'
    assert files['files[]'][0].read() == b'abcdef'
    assert files['files[]'][1].filename == 'MyText.txt'
    assert files['files[]'][1].content_type == b'text/plain'
    assert files['files[]'][1].read() == b'ghi'
