import orjson
import typing as t
from urllib.parse import parse_qsl
from horseman.asgi.parsers.parser import BodyParser
from horseman.wsgi.parsers.multipart import Multipart
from horseman.datastructures import Data
from horseman.types import Boundary, Charset, MIMEType


parser = BodyParser()


@parser.register('application/json')
async def json_parser(body: t.AsyncGenerator, mimetype: MIMEType,
                      charset: Charset = 'utf-8') -> Data:
    data = b''
    async for chunk in body:
        data += chunk
    if not data:
        raise ValueError('The body of the request is empty.')
    try:
        jsondata = orjson.loads(data.decode(charset))
        return Data(json=jsondata)
    except orjson.JSONDecodeError:
        raise ValueError('Unparsable JSON body.')


@parser.register('multipart/form-data')
async def multipart_parser(body: t.AsyncGenerator, mimetype: MIMEType,
                           boundary: t.Optional[Boundary] = None) -> Data:
    if boundary is None:
        raise ValueError('Missing boundary in Content-Type.')
    content_parser = Multipart(f";boundary={boundary}")
    async for chunk in body:
        try:
            content_parser.feed_data(chunk)
        except ValueError:
            raise ValueError('Unparsable multipart body.')
    return Data(form=content_parser.form)


@parser.register('application/x-www-form-urlencoded')
async def urlencoded_parser(body: t.AsyncGenerator, mimetype: MIMEType,
                            charset: Charset = 'utf-8') -> Data:
    data = b''
    async for chunk in body:
        data += chunk
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
