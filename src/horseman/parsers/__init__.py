import re
import orjson
import typing as t
from http import HTTPStatus
from urllib.parse import parse_qsl
from horseman.parsers.multipart import Multipart
from horseman.http import HTTPError, ContentType
from horseman.types import Charset, MIMEType


MIME_TYPE_REGEX = re.compile(r"^multipart|[-\w.]+/[-\w.\+]+$")


class Data(t.NamedTuple):
    form: t.Optional[t.Iterable[t.Tuple[str, t.Any]]] = None
    json: t.Optional[t.Union[t.Dict, t.List]] = None  # not too specific


Boundary = str
Parser = t.Callable[[
    t.IO, MIMEType, t.Optional[t.Union[Charset, Boundary]]
], Data]


class BodyParser:

    __slots__ = ('parsers',)

    def __init__(self):
        self.parsers = {}

    def register(self, mimetype: MIMEType):
        if not MIME_TYPE_REGEX.fullmatch(mimetype):
            raise ValueError(f'{mimetype!r} is not a valid MIME Type.')

        def registration(parser: Parser) -> Parser:
            self.parsers[mimetype.lower()] = parser
            return parser
        return registration

    def get(self, mimetype: MIMEType) -> t.Optional[Parser]:
        return self.parsers.get(mimetype)

    def __call__(self, body: t.IO, header: t.Union[str, ContentType]) -> Data:
        if not isinstance(header, ContentType):
            content_type = ContentType.from_http_header(header)
        else:
            content_type = header
        parser = self.get(content_type.mimetype)
        if parser is None:
            raise HTTPError(
                HTTPStatus.BAD_REQUEST,
                f'Unknown content type: {content_type.mimetype!r}.'
            )
        try:
            return parser(
                body, content_type.mimetype, **content_type.options)
        except ValueError as exc:
            raise HTTPError(HTTPStatus.BAD_REQUEST, str(exc))


parser = BodyParser()


@parser.register('application/json')
def json_parser(body: t.IO, mimetype: MIMEType,
                charset: Charset = 'utf-8') -> Data:
    data = body.read()
    if not data:
        raise ValueError('The body of the request is empty.')
    try:
        jsondata = orjson.loads(data.decode(charset))
        return Data(json=jsondata)
    except orjson.JSONDecodeError:
        raise ValueError('Unparsable JSON body.')


@parser.register('multipart/form-data')
def multipart_parser(body: t.IO, mimetype: MIMEType,
                     boundary: t.Optional[str] = None) -> Data:
    if boundary is None:
        raise ValueError('Missing boundary in Content-Type.')
    content_parser = Multipart(f";boundary={boundary}")
    while chunk := body.read(8192):
        try:
            content_parser.feed_data(chunk)
        except ValueError:
            raise ValueError('Unparsable multipart body.')
    return Data(form=content_parser.form)


@parser.register('application/x-www-form-urlencoded')
def urlencoded_parser(body: t.IO, mimetype: MIMEType,
                      charset: Charset = 'utf-8') -> Data:
    data = body.read()
    if not data:
        raise ValueError('The body of the request is empty.')
    try:
        form = parse_qsl(
            data.decode(charset),
            keep_blank_values=True,
            strict_parsing=True
        )
    except UnicodeDecodeError:
        raise ValueError(f'Failed to decode using charset {charset!r}.')
    return Data(form=form)
