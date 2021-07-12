import hamcrest
from horseman.response import Headers


def test_empty_headers():
    headers = Headers()
    assert list(headers.items()) == []
    assert len(headers) == 0


def test_add_headers():
    headers = Headers({'Link': 'test'})
    assert list(headers.items()) == [('Link', 'test')]
    assert len(headers) == 1

    headers.add('Link', 'Another test')
    assert list(headers.items()) == [
        ('Link', 'test'),
        ('Link', 'Another test')
    ]
    assert len(headers) == 2


def test_cookies():
    headers = Headers()
    headers.cookies.set('test', "{'this': 'is json'}")
    assert 'test' in headers.cookies
    assert list(headers.items()) == [
        ('Set-Cookie', 'test="{\'this\': \'is json\'}"; Path=/')
    ]


def test_headers_coalescence():
    """Coalescence of headers does NOT garanty order of headers.
    It garanties the order of the header values, though.
    """
    headers = Headers([
        ('Link', 'test'),
        ('X-Robots-Tag', 'noarchive'),
        ('X-Robots-Tag', 'google: noindex, nosnippet')
    ])

    hamcrest.assert_that(
        list(headers.coalesced_items()),
        hamcrest.contains_inanyorder(
            ('Link', 'test'),
            ('X-Robots-Tag', 'noarchive, google: noindex, nosnippet'),
        )
    )

    headers.add('X-Robots-Tag', 'otherbot: noindex')
    hamcrest.assert_that(
        list(headers.coalesced_items()),
        hamcrest.contains_inanyorder(
            ('Link', 'test'),
            ('X-Robots-Tag', 'noarchive, google: noindex, nosnippet, '
                             'otherbot: noindex'),
        )
    )

    assert list(headers.items()) == [
        ('Link', 'test'),
        ('X-Robots-Tag', 'noarchive'),
        ('X-Robots-Tag', 'google: noindex, nosnippet'),
        ('X-Robots-Tag', 'otherbot: noindex'),
    ]


def test_headers_coalescence_with_cookies():
    headers = Headers()
    headers.cookies.set('test', "{'this': 'is json'}")
    headers.add('X-Robots-Tag', 'otherbot: noindex')

    hamcrest.assert_that(
        list(headers.coalesced_items()),
        hamcrest.contains_inanyorder(
            ('X-Robots-Tag', 'otherbot: noindex'),
            ('Set-Cookie', 'test="{\'this\': \'is json\'}"; Path=/')
        )
    )

    headers.add('Set-Cookie', 'other=foobar')
    hamcrest.assert_that(
        list(headers.coalesced_items()),
        hamcrest.contains_inanyorder(
            ('X-Robots-Tag', 'otherbot: noindex'),
            ('Set-Cookie', 'other=foobar, '
                           'test="{\'this\': \'is json\'}"; Path=/')
        )
    )
