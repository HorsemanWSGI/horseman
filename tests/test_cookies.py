from horseman.http import Cookies


def test_request_parse_cookies():
    from webtest.app import TestRequest as Request

    # A simple cookie
    request = Request(environ={}, cookies={'key': 'value'})
    cookies = Cookies.from_environ(request.environ)
    assert cookies['key'] == 'value'

    # No cookie
    request = Request(environ={})
    cookies = Cookies.from_environ(request.environ)
    assert not cookies
