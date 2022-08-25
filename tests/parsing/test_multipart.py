import pytest
from io import BytesIO
from webtest.app import TestApp as App
from horseman.parsers import parser
from horseman.http import HTTPError


BAD_MULTIPART = (
    b"""--foo\r\nContent->Disposition: form-data; """
    b"""name="text1"\r\n\r\n'abc\r\n--foo--\r\n"""
)

BAD_MULTIPART_NO_CONTENT_DISPOSITION = (
    b"""------------a_BoUnDaRy7283067873172754$\r\n"""
    b"""Content-Disposition: ; name="test"\r\n\r\nsome value\r\n"""
    b"""------------a_BoUnDaRy7283067873172754$--\r\n"""
)


def test_multipart():

    app = App(None)
    content_type, body = app.encode_multipart([
        ('test', 'some value'),
        ('test', 'some other value'),
        ('foo', 'bar')
    ], [])

    data = parser(BytesIO(body), content_type)
    assert len(data.form) == 3
    assert data.form == [
        ('test', 'some value'),
        ('test', 'some other value'),
        ('foo', 'bar')
    ]


def test_empty_multipart():

    app = App(None)
    content_type, body = app.encode_multipart([
        ('test', ''),
        ('test', ''),
        ('foo', 'bar')
    ], [])
    data = parser(BytesIO(body), content_type)
    assert len(data.form) == 1
    assert data.form == [
        ('foo', 'bar')
    ]


def test_multipart_empty_files_empty_name():
    app = App(None)
    content_type, body = app.encode_multipart(
        [],
        [('test', "", b'', "application/octet")],
    )
    data = parser(BytesIO(body), content_type)
    assert data.form == []

    content_type, body = app.encode_multipart(
        [],
        [('test', "", b'', "application/octet"),
         ('test2', "", b'', "application/octet")],
    )
    data = parser(BytesIO(body), content_type)
    assert data.form == []


def test_multipart_empty_files_mixed():
    app = App(None)
    content_type, body = app.encode_multipart(
        [],
        [('test', "name", b'', "application/octet"),
         ('test2', "", b'content', "application/octet"),
         ('test3', "", b'', "application/octet")],
    )
    data = parser(BytesIO(body), content_type)
    assert len(data.form) == 2
    _, file1 = data.form[0]
    _, file2 = data.form[1]
    assert file1.filename == "name"
    assert file2.read() == b'content'
    assert file2.filename != ''


def test_multipart_empty_filename_generation():
    app = App(None)
    content_type, body = app.encode_multipart(
        [],
        [('test', "", b'content', "application/octet"),
         ('test', "", b'content', "application/octet")]
    )
    data = parser(BytesIO(body), content_type)
    _, file1 = data.form[0]
    _, file2 = data.form[1]
    assert file1.filename != file2.filename
    assert file1.filename != ''


def test_multipart_files():

    app = App(None)
    content_type, body = app.encode_multipart(
        [('test', b'some value')],
        [('files', "baz-\xe9.png", b'abcdef', 'image/png'),
         ('files', "MyText.txt", b'ghi', 'text/plain')]
    )

    data = parser(BytesIO(body), content_type)
    uploaded = data.form[1:]
    assert len(uploaded) == 2
    name, obj = uploaded[0]
    assert obj.filename == 'baz-é.png'
    assert obj.content_type == b'image/png'
    assert obj.read() == b'abcdef'

    name, obj = uploaded[1]
    assert obj.filename == 'MyText.txt'
    assert obj.content_type == b'text/plain'
    assert obj.read() == b'ghi'


def test_wrong_multipart():
    with pytest.raises(HTTPError) as exc:
        parser(BytesIO(b'test'), "multipart/form-data")
    assert exc.value.status == 400
    assert exc.value.body == 'Missing boundary in Content-Type.'

    with pytest.raises(HTTPError) as exc:
        parser(BytesIO(BAD_MULTIPART),
               "multipart/form-data; boundary=--foo")
    assert exc.value.status == 400
    assert exc.value.body == 'Unparsable multipart body.'


def test_wrong_multipart_no_content_disposition():

    with pytest.raises(HTTPError) as exc:
        parser(BytesIO(BAD_MULTIPART_NO_CONTENT_DISPOSITION),
               'multipart/form-data; '
               'boundary=----------a_BoUnDaRy7283067873172754$')

    assert exc.value.status == 400
    assert exc.value.body == ('Unparsable multipart body.')
