import pytest
from io import BytesIO
from horseman.parsers import BodyParser, Data
from horseman.http import HTTPError, ContentType


def test_parser_invalid_registration():
    parser = BodyParser()

    with pytest.raises(ValueError) as exc:

        @parser.register('foo')
        def test(body, mimetype, **options):
            pass

    assert str(exc.value) == "'foo' is not a valid MIME Type."


def test_parser_registration():
    parser = BodyParser()

    @parser.register('foo/bar')
    def test(body, mimetype, **options):
        pass

    assert parser.get('foo/bar') == test


def test_parser_registration_override():
    parser = BodyParser()

    @parser.register('foo/bar')
    def test(body, mimetype, **options):
        pass

    assert parser.get('foo/bar') == test

    @parser.register('foo/bar')
    def test2(body, mimetype, **options):
        pass

    assert parser.get('foo/bar') == test2


def test_unknown_parser():
    parser = BodyParser()

    with pytest.raises(HTTPError) as exc:
        parser(BytesIO(b'body'), 'foo/bar')

    assert exc.value.status == 400
    assert exc.value.body == "Unknown content type: 'foo/bar'."

    @parser.register('foo/bar')
    def test(body, mimetype, **options):
        return Data()

    data = parser(BytesIO(b'body'), 'foo/bar')
    assert isinstance(data, Data)

    data = parser(BytesIO(b'body'), 'foo/bar; charset=UTF-8')
    assert isinstance(data, Data)


def test_parser_with_mimetype():
    parser = BodyParser()
    contenttype = ContentType('foo/bar', {})

    @parser.register('foo/bar')
    def test(body, mimetype, **options):
        return Data()

    data = parser(BytesIO(b'body'), contenttype)
    assert isinstance(data, Data)
