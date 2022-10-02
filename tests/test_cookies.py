from biscuits import Cookie
from horseman.datastructures import Cookies


def test_request_parse_cookies():
    from webtest.app import TestRequest as Request

    # A simple cookie
    cookie = Cookie(name='key', value='value')
    cookies = Cookies.from_string(str(cookie))
    assert cookies['key'] == 'value'

    # No cookie
    cookies = Cookies.from_string("")
    assert not cookies
