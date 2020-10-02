from http import HTTPStatus
from horseman.parsing.multipart import Multipart
from horseman.http import HTTPError, Query
try:
    # In case you use json heavily, we recommend installing
    # https://pypi.python.org/pypi/ujson for better performances.
    import ujson as json
    JSONDecodeError = ValueError
except ImportError:
    import json as json
    from json.decoder import JSONDecodeError


def _json(body, content_type: str) -> dict:
    data = body.read()
    try:
        jsondata = json.loads(data)
        # We currently do not support non-object body
        assert isinstance(jsondata, dict)
        return jsondata
    except (UnicodeDecodeError, JSONDecodeError):
        raise HTTPError(HTTPStatus.BAD_REQUEST, 'Unparsable JSON body')


def _multipart(body, content_type: str, chunksize: int=4096) -> dict:
    content_parser = Multipart(content_type)
    content_parser.feed_data(body.read())
    return {
        **content_parser.form.to_dict(),
        **content_parser.files.to_dict()
    }


def _urlencoded(body, content_type: str) -> dict:
    data = body.read()
    try:
        form = Query.from_value(data.decode())
    except ValueError:
        raise HTTPError(HTTPStatus.BAD_REQUEST, 'Unparsable urlencoded body')
    return form.to_dict()


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
