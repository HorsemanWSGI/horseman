import pytest
from io import BytesIO
from horseman.parsers import Data, urlencoded_parser


def test_urlencoded():
    body = BytesIO(b'name=MacBeth&thane=Cawdor&thane=Glamis')
    data = urlencoded_parser(body, 'application/x-www-form-urlencoded')
    assert data == Data(
        form={
            'name': ['MacBeth'],
            'thane': ['Cawdor', 'Glamis']
        },
        files=None,
        json=None
    )


def test_urlencoded_charset():
    body = BytesIO("name=Älfùr".encode('utf-8'))
    data = urlencoded_parser(body, 'application/x-www-form-urlencoded')
    assert data == Data(
        form={'name': ['Älfùr']},
        files=None,
        json=None
    )

    body = BytesIO("name=Älfùr".encode('latin-1'))
    with pytest.raises(ValueError) as exc:
        urlencoded_parser(body, 'application/x-www-form-urlencoded')
    assert str(exc.value) == "Failed to decode using charset 'utf-8'."

    body = BytesIO("name=Älfùr".encode('latin-1'))
    data = urlencoded_parser(
        body, 'application/x-www-form-urlencoded', charset='latin-1')
    assert data == Data(
        form={'name': ['Älfùr']},
        files=None,
        json=None
    )


def test_wrong_urlencoded():
    body = BytesIO(b'foo')
    with pytest.raises(ValueError) as exc:
        urlencoded_parser(body, 'application/x-www-form-urlencoded')
    assert str(exc.value) == "bad query field: 'foo'"
