import pytest
from horseman.parsers import parser


def test_parser_invalid_registration():

    with pytest.raises(ValueError) as exc:

        @parser.register('foo')
        def test(body, mimetype):
            pass

    assert str(exc.value) == "'foo' is not a valid MIME Type"


def test_parser_registration():

    @parser.register('foo/bar')
    def test(body, mimetype):
        pass

    assert parser.get('foo/bar') == test


def test_parser_registration_override():

    @parser.register('foo/bar')
    def test(body, mimetype):
        pass

    assert parser.get('foo/bar') == test

    @parser.register('foo/bar')
    def test2(body, mimetype):
        pass

    assert parser.get('foo/bar') == test2
