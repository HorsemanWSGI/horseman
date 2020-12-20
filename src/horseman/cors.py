from functools import wraps
from typing import Iterable
from horseman import HTTPCode


def allow_origins(origins: str, codes: Iterable[HTTPCode] = None):
    def cors_wrapper(method):
        @wraps(method)
        def add_cors_header(*args, **kwargs):
            response = method(*args, **kwargs)
            if codes and response.status not in codes:
                return response
            response.headers["Access-Control-Allow-Origin"] = origins
            return response
        return add_cors_header
    return cors_wrapper
