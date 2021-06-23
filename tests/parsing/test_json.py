import pytest
from io import BytesIO
from horseman.parsers import Data, json_parser


def test_empty_json():
    body = BytesIO(b'')
    with pytest.raises(ValueError) as exc:
        json_parser(body, 'application/json')
    assert str(exc.value) == "The body of the request is empty."


def test_json():
    body = BytesIO(b'{"foo": "bar"}')
    data = json_parser(body, 'application/json')
    assert data == Data(
        form=None,
        files=None,
        json={'foo': 'bar'}
    )


def test_json_charset():
    body = BytesIO('{"name": "Älfùr"}'.encode('utf-8'))
    data = json_parser(body, 'application/json')
    assert data == Data(
        form=None,
        files=None,
        json={'name': 'Älfùr'}
    )

    body = BytesIO('{"name": "Älfùr"}'.encode('latin-1'))
    with pytest.raises(ValueError) as exc:
        json_parser(body, 'application/json')
    assert str(exc.value) == (
        "'utf-8' codec can't decode byte 0xc4 in position 10: "
        "invalid continuation byte")

    body = BytesIO('{"name": "Älfùr"}'.encode('latin-1'))
    data = json_parser(body, 'application/json', charset='latin-1')
    assert data == Data(
        form=None,
        files=None,
        json={'name': 'Älfùr'}
    )


def test_wrong_json():
    body = BytesIO(b'foo')
    with pytest.raises(ValueError) as exc:
        json_parser(body, 'application/json')
    assert str(exc.value) == "Unparsable JSON body."
