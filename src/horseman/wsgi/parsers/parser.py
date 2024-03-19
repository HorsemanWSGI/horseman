import re
import typing as t
from http import HTTPStatus
from horseman.exceptions import HTTPError
from horseman.datastructures import ContentType, Data
from horseman.types import Boundary, Charset, MIMEType


MIME_TYPE_REGEX = re.compile(r"^multipart|[-\w.]+/[-\w.\+]+$")

Parser = t.Callable[[
    t.IO, MIMEType, t.Optional[t.Union[Charset, Boundary]]
], Data]


class BodyParser(t.Dict[MIMEType, Parser]):

    __slots__ = ()

    def register(self, mimetype: str):
        if not MIME_TYPE_REGEX.fullmatch(mimetype):
            raise ValueError(f'{mimetype!r} is not a valid MIME Type.')

        def registration(parser: Parser) -> Parser:
            self[mimetype.lower()] = parser
            return parser
        return registration

    def parse(self, body: t.IO, header: t.Union[str, ContentType]) -> Data:
        content_type = ContentType(header)  # idempotent
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
