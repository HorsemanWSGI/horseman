from http import HTTPStatus
from urllib.parse import parse_qs
from multidict import MultiDict
from horseman.parsing.multipart import Multipart
from horseman import HTTPCode, HTTPError
try:
    # In case you use json heavily, we recommend installing
    # https://pypi.python.org/pypi/ujson for better performances.
    import ujson as json
    JSONDecodeError = ValueError
except ImportError:
    import json as json
    from json.decoder import JSONDecodeError


def query(query_string):
    parsed_qs = parse_qs(query_string, keep_blank_values=True)
    return MultiDict(parsed_qs)


def _json(body, content_type: str):
    data = body.read()
    try:
        return json.loads(data), None
    except (UnicodeDecodeError, JSONDecodeError):
        raise HTTPError(HTTPStatus.BAD_REQUEST, 'Unparsable JSON body')


def _multipart(body, content_type: str, chunksize: int=4096):
    parser, data = Multipart.parse(content_type)
    try:
        for chunk in body.read(4096):
            if not chunk:
                break
            parser.feed_data(chunk)
    except ValueError:
        raise HTTPError(HTTPStatus.BAD_REQUEST, 'Unparsable multipart body')
    return data.form, data.files


def _urlencoded(body, content_type: str):
    data = body.read()
    try:
        parsed_qs = parse_qs(
            data.decode(), keep_blank_values=True, strict_parsing=True)
    except ValueError:
        raise HTTPError(HTTPStatus.BAD_REQUEST, 'Unparsable urlencoded body')
    return MultiDict(parsed_qs), None


PARSERS = {
    'multipart/form-data': _multipart,
    'application/x-www-form-urlencoded': _urlencoded,
    'application/json': _json
}


def parse(body, content_type: str):
    parser = PARSERS.get(content_type)
    if parser is None:
        raise HTTPError(
            HTTPStatus.BAD_REQUEST, f'Unknown content type: {content_type}')
    return parser(body, content_type)
