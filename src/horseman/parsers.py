import orjson
import re
import typing as t
from http import HTTPStatus
from urllib.parse import parse_qsl
from kettu.parsers.multipart import Multipart
from kettu.exceptions import HTTPError
from kettu.datastructures import Data
from kettu.headers import ContentType
from kettu.types import Boundary, Charset, MIMEType


MIME_TYPE_REGEX = re.compile(r"^multipart|[-\w.]+/[-\w.\+]+$")

Parser = t.Callable[[t.IO, MIMEType, Charset | Boundary | None], Data]


class BodyParser(dict[MIMEType, Parser]):

    def register(self, mimetype: str):
        if not MIME_TYPE_REGEX.fullmatch(mimetype):
            raise ValueError(f"{mimetype!r} is not a valid MIME Type.")

        def registration(parser: Parser) -> Parser:
            self[mimetype.lower()] = parser
            return parser

        return registration

    def parse(self, body: t.IO, header: str | ContentType) -> Data:
        if isinstance(header, str):
            header = ContentType.from_string(header)
        parser = self.get(header.mimetype)
        if parser is None:
            raise HTTPError(
                HTTPStatus.BAD_REQUEST,
                f"Unknown content type: {header.mimetype!r}.",
            )
        try:
            return parser(body, header.mimetype, **header.options)
        except ValueError as exc:
            raise HTTPError(HTTPStatus.BAD_REQUEST, str(exc))


parser = BodyParser()


@parser.register("application/json")
def json_parser(
        body: t.IO,
        mimetype: MIMEType,
        charset: Charset = "utf-8"
) -> Data:
    data = body.read()
    if not data:
        raise ValueError("The body of the request is empty.")
    try:
        jsondata = orjson.loads(data.decode(charset))
        return Data(json=jsondata)
    except orjson.JSONDecodeError:
        raise ValueError("Unparsable JSON body.")


@parser.register("multipart/form-data")
def multipart_parser(
    body: t.IO, mimetype: MIMEType, boundary: t.Optional[Boundary] = None
) -> Data:
    if boundary is None:
        raise ValueError("Missing boundary in Content-Type.")
    content_parser = Multipart(f";boundary={boundary}")
    while chunk := body.read(8192):
        try:
            content_parser.feed_data(chunk)
        except ValueError:
            raise ValueError("Unparsable multipart body.")
    return Data(form=content_parser.form)


@parser.register("application/x-www-form-urlencoded")
def urlencoded_parser(
    body: t.IO, mimetype: MIMEType, charset: Charset = "utf-8"
) -> Data:
    data = body.read()
    if not data:
        raise ValueError("The body of the request is empty.")
    try:
        form = parse_qsl(
            data.decode(charset), keep_blank_values=True, strict_parsing=True
        )
    except UnicodeDecodeError:
        raise ValueError(f"Failed to decode using charset {charset!r}.")
    return Data(form=form)
