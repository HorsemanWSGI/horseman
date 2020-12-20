from http import HTTPStatus
from typing import Dict, List, NamedTuple, Optional, Union
from horseman.parsing.multipart import Multipart
from horseman.http import HTTPError, Query, Multidict
try:
    # In case you use json heavily, we recommend installing
    # https://pypi.python.org/pypi/ujson for better performances.
    import ujson as json
    JSONDecodeError = ValueError
except ImportError:
    import json as json
    from json.decoder import JSONDecodeError


class Data(NamedTuple):
    form: Optional[Multidict]
    files: Optional[Multidict]
    json: Optional[Union[Dict, List]]  # not too specific


def _json(body, content_type: str) -> Data:
    data = body.read()
    try:
        jsondata = json.loads(data)
        return Data(form=None, files=None, json=jsondata)
    except (UnicodeDecodeError, JSONDecodeError):
        raise HTTPError(
            HTTPStatus.BAD_REQUEST,
            'Unparsable JSON body'
        )


def _multipart(body, content_type: str, chunksize: int = 4096) -> Data:
    content_parser = Multipart(content_type)
    content_parser.feed_data(body.read())
    return Data(
        form=content_parser.form,
        files=content_parser.files,
        json=None
    )


def _urlencoded(body, content_type: str) -> Data:
    data = body.read()
    try:
        form = Query.from_value(data.decode())
    except ValueError:
        raise HTTPError(
            HTTPStatus.BAD_REQUEST,
            'Unparsable urlencoded body'
        )
    return Data(form=form, files=None, json=None)


PARSERS = {
    'multipart/form-data': _multipart,
    'application/x-www-form-urlencoded': _urlencoded,
    'application/json': _json
}


def parse(body, content_type: str) -> Data:
    identifier = content_type.split(';', 1)[0].strip()
    parser = PARSERS.get(identifier)
    if parser is None:
        raise HTTPError(
            HTTPStatus.BAD_REQUEST,
            f'Unknown content type: {content_type}'
        )
    return parser(body, content_type)
