from functools import wraps


def allow_origins(origins, codes=None):
    def cors_wrapper(method):
        @wraps(method)
        def add_cors_header(*args, **kwargs):
            res = method(*args, **kwargs)
            if codes and not res.status_int in codes:
                return res
            res.headers["Access-Control-Allow-Origin"] = origins
            return res
        return add_cors_header
    return cors_wrapper
