import re
import cgi
import orjson
from functools import wraps
from http import HTTPStatus
from typing import TypeVar, Optional, Union
from typing import Dict, List, NamedTuple, IO, Callable
from horseman.parsers.multipart import Multipart
from horseman.http import HTTPError, Query, Multidict


MIMEType = TypeVar('MIMEType', str, bytes)


class Data(NamedTuple):
    form: Optional[Multidict] = None
    files: Optional[Multidict] = None
    json: Optional[Union[Dict, List]] = None  # not too specific


class ContentType(NamedTuple):
    raw: str
    mimetype: MIMEType
    options: dict

    @classmethod
    def from_http_header(cls, header: str):
        return cls(header, *cgi.parse_header(ct))




Parser = Callable[[IO, MIMEType], Data]
MIME_TYPE_REGEX = re.compile(r"^multipart|[-\w.]+/[-\w.\+]+$")


class BodyParser(Parser):

    __slots__ = ('parsers',)

    def __init__(self):
        self.parsers = {}

    def register(self, mimetype: MIMEType):
        if not MIME_TYPE_REGEX.fullmatch(mimetype):
            raise ValueError(f'{mimetype!r} is not a valid MIME Type')

        def registration(parser: Parser) -> Parser:
            self.parsers[mimetype.lower()] = parser
            return parser
        return registration

    def get(self, mimetype: MIMEType) -> Optional[Parser]:
        return self.parsers.get(mimetype.lower())

    def __call__(self, body: IO, mimetype: MIMEType) -> Data:
        identifier = mimetype.split(';', 1)[0].strip()
        parser = self.get(identifier)
        if parser is None:
            raise HTTPError(
                HTTPStatus.BAD_REQUEST,
                f'Unknown content type: {mimetype}.'
            )
        try:
            return parser(body, mimetype)
        except ValueError as exc:
            raise HTTPError(HTTPStatus.BAD_REQUEST, str(exc))


parser = BodyParser()


@parser.register('application/json')
def json_parser(body: IO, mimetype: MIMEType) -> Data:
    data = body.read()
    try:
        jsondata = orjson.loads(data)
        return Data(json=jsondata)
    except orjson.JSONDecodeError:
        raise ValueError('Unparsable JSON body')


@parser.register('multipart/form-data')
def multipart_parser(body: IO, mimetype: MIMEType) -> Data:
    content_parser = Multipart(mimetype)
    while chunk := body.read(8128):
        try:
            content_parser.feed_data(chunk)
        except ValueError:
            raise ValueError('Unparsable multipart body.')
    return Data(form=content_parser.form, files=content_parser.files)


@parser.register('application/x-www-form-urlencoded')
def urlencoded_parser(body: IO, mimetype: MIMEType) -> Data:
    data = body.read()
    form = Query.from_value(data.decode())
    return Data(form=form)
