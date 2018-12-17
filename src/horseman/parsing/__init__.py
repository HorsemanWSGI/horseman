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


def json(body):
    data = body.read()
    try:
        return json.loads(data)
    except (UnicodeDecodeError, JSONDecodeError):
        raise HttpError(HTTPStatus.BAD_REQUEST, 'Unparsable JSON body')


def query(query_string):
    parsed_qs = parse_qs(query_string, keep_blank_values=True)
    return MultiDict(parsed_qs)


def parse_multipart(body, content_type: str, chunksize: int=4096):
    parser, data = Multipart.parse(content_type)
    try:
        for chunk in body.read(4096):
            if not chunk:
                break
            parser.feed_data(chunk)
    except ValueError:
        raise HTTPError(HTTPStatus.BAD_REQUEST, 'Unparsable multipart body')
    return data.form, data.files


def parse_urlencoded(body):
    data = body.read()
    try:
        parsed_qs = parse_qs(
            data.decode(), keep_blank_values=True, strict_parsing=True)
    except ValueError:
        raise HttpError(HTTPStatus.BAD_REQUEST, 'Unparsable urlencoded body')
    return MultiDict(parsed_qs), None


def parse(body, content_type: str):
    if 'multipart/form-data' in self.content_type:
        return parse_multipart(body, content_type)
    elif 'application/x-www-form-urlencoded' in self.content_type:
        return parse_urlencoded(body)
    raise HttpError(HTTPStatus.BAD_REQUEST, 'Unknown content type')
