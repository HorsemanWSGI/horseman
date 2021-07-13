import pytest
from io import BytesIO
from horseman.http import Query
from horseman.parsers import Data, urlencoded_parser


def test_empty_urlencoded():
    body = BytesIO(b'')
    with pytest.raises(ValueError) as exc:
        urlencoded_parser(body, 'application/x-www-form-urlencoded')
    assert str(exc.value) == "The body of the request is empty."


def test_urlencoded():
    body = BytesIO(b'name=MacBeth&thane=Cawdor&thane=Glamis')
    data = urlencoded_parser(body, 'application/x-www-form-urlencoded')
    assert isinstance(data, Data)
    assert data.files is None
    assert data.json is None
    assert isinstance(data.form, Query)
    assert tuple(data.form.pairs()) == (
        ('name', 'MacBeth'),
        ('thane', 'Cawdor'),
        ('thane', 'Glamis')
    )


def test_urlencoded_charset():
    body = BytesIO("name=Älfùr".encode('utf-8'))
    data = urlencoded_parser(body, 'application/x-www-form-urlencoded')
    assert isinstance(data, Data)
    assert data.files is None
    assert data.json is None
    assert isinstance(data.form, Query)
    assert tuple(data.form.pairs()) == (
        ('name', 'Älfùr'),
    )

    body = BytesIO("name=Älfùr".encode('latin-1'))
    with pytest.raises(ValueError) as exc:
        urlencoded_parser(body, 'application/x-www-form-urlencoded')
    assert str(exc.value) == "Failed to decode using charset 'utf-8'."

    body = BytesIO("name=Älfùr".encode('latin-1'))
    data = urlencoded_parser(
        body, 'application/x-www-form-urlencoded', charset='latin-1')
    assert isinstance(data, Data)
    assert data.files is None
    assert data.json is None
    assert isinstance(data.form, Query)
    assert tuple(data.form.pairs()) == (
        ('name', 'Älfùr'),
    )


def test_wrong_urlencoded():
    body = BytesIO(b'foo')
    with pytest.raises(ValueError) as exc:
        urlencoded_parser(body, 'application/x-www-form-urlencoded')
    assert str(exc.value) == "bad query field: 'foo'"
