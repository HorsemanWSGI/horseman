import pytest
from io import BytesIO
from horseman.parsers import parser
from horseman.http import HTTPError


BAD_MULTIPART = b"""
--foo
Content->Disposition: form-data; name="text1"

'abc\r\n--foo--
"""

BAD_MULTIPART_NO_CONTENT_DISPOSITION = b"""
------------a_BoUnDaRy7283067873172754$
Content-Disposition: ; name="test"

some value
------------a_BoUnDaRy7283067873172754$--
"""


def test_multipart():
    from webtest.app import TestApp

    app = TestApp(None)
    content_type, body = app.encode_multipart([
        ('test', 'some value'),
        ('test', 'some other value'),
        ('foo', 'bar')
    ], [])

    data = parser(BytesIO(body), content_type)
    assert len(data.form) == 3
    assert list(data.form.items()) == [
        ('test', 'some value'),
        ('test', 'some other value'),
        ('foo', 'bar')
    ]
    assert data.form.getone('foo') == 'bar'
    assert data.form.getall('test') == ['some value', 'some other value']


def test_multipart_files():
    from webtest.app import TestApp

    app = TestApp(None)
    content_type, body = app.encode_multipart(
        [('test', b'some value')],
        [('files', "baz-\xe9.png", b'abcdef', 'image/png'),
         ('files', "MyText.txt", b'ghi', 'text/plain')]
    )

    data = parser(BytesIO(body), content_type)
    uploaded = data.files.getall('files')
    assert len(uploaded) == 2
    assert uploaded[0].filename == 'baz-é.png'
    assert uploaded[0].content_type == b'image/png'
    assert uploaded[0].read() == b'abcdef'
    assert uploaded[1].filename == 'MyText.txt'
    assert uploaded[1].content_type == b'text/plain'
    assert uploaded[1].read() == b'ghi'


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
