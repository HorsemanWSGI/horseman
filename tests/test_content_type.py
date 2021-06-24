from horseman.http import ContentType


def test_content_type():

    header = (
        '''Message/Partial; number=2; total=3; '''
        '''id="oc=jpbe0M2Yt4s@thumper.bellcore.com";'''
    )

    ct = ContentType.from_http_header(header)
    assert ct.mimetype == "Message/Partial"
    assert ct.options == {
        'number': '2',
        'total': '3',
        'id': 'oc=jpbe0M2Yt4s@thumper.bellcore.com'
    }
