from horseman.datastructures import ContentType


def test_content_type():

    header = (
        '''Message/Partial; number=2; total=3; '''
        '''id="oc=jpbe0M2Yt4s@thumper.bellcore.com";'''
    )

    ct = ContentType(header)
    assert ct.mimetype == "Message/Partial"
    assert ct.options == {
        'number': '2',
        'total': '3',
        'id': 'oc=jpbe0M2Yt4s@thumper.bellcore.com'
    }


def test_idempotency():
    header = (
        '''Message/Partial; number=2; total=3; '''
        '''id="oc=jpbe0M2Yt4s@thumper.bellcore.com";'''
    )
    ct = ContentType(header)
    assert ContentType(ct) is ct
