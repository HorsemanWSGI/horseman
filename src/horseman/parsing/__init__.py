from http import HTTPStatus
from urllib.parse import parse_qs
from horseman.parsing.multipart import Multipart
from horseman.http import HTTPError, Multidict, Files
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
    return Multidict(parsed_qs)


def _json(body, content_type: str):
    data = body.getvalue()
    try:
        return json.loads(data), Files()
    except (UnicodeDecodeError, JSONDecodeError):
        raise HTTPError(HTTPStatus.BAD_REQUEST, 'Unparsable JSON body')


def _multipart(body, content_type: str, chunksize: int=4096):
    content_parser = Multipart(content_type)
    content_parser.feed_data(body.getvalue())
    return content_parser.form, content_parser.files


def _urlencoded(body, content_type: str):
    data = body.read()
    try:
        parsed_qs = parse_qs(
            data.decode(), keep_blank_values=True, strict_parsing=True)
    except ValueError:
        raise HTTPError(HTTPStatus.BAD_REQUEST, 'Unparsable urlencoded body')
    return Multidict(parsed_qs), Files()


PARSERS = {
    'multipart/form-data': _multipart,
    'application/x-www-form-urlencoded': _urlencoded,
    'application/json': _json
}


def parse(body, content_type: str):
    identifier = content_type.split(';', 1)[0].strip()
    parser = PARSERS.get(identifier)
    if parser is None:
        raise HTTPError(
            HTTPStatus.BAD_REQUEST, f'Unknown content type: {content_type}')
    return parser(body, content_type)
