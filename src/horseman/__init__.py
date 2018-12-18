from http import HTTPStatus
from typing import TypeVar


HTTPCode = TypeVar('HttpCode', HTTPStatus, int)


class HTTPError(Exception):

    __slots__ = ('status', 'message')

    def __init__(self, http_code: HTTPCode, message: str=None):
        self.status = HTTPStatus(http_code)
        self.message = message or self.status.description
