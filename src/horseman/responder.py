# -*- coding: utf-8 -*-

from webob import exc, Response


HTTPRESPONSES = {
#HTTP OK
    0: Response,
    200: exc.HTTPOk,
    201: exc.HTTPCreated,
    202: exc.HTTPAccepted,
    203: exc.HTTPNonAuthoritativeInformation,
    204: exc.HTTPNoContent,
    205: exc.HTTPResetContent,
    206: exc.HTTPPartialContent,

#HTTP Redirection
    
    300: exc.HTTPMultipleChoices,
    301: exc.HTTPMovedPermanently,
    302: exc.HTTPFound,
    303: exc.HTTPSeeOther,
    304: exc.HTTPNotModified,
    305: exc.HTTPUseProxy,
    307: exc.HTTPTemporaryRedirect,
    308: exc.HTTPPermanentRedirect,

#HTTP Error: Client Error

    400: exc.HTTPBadRequest,
    401: exc.HTTPUnauthorized,
    402: exc.HTTPPaymentRequired,
    403: exc.HTTPForbidden,
    404: exc.HTTPNotFound,
    405: exc.HTTPMethodNotAllowed,
    406: exc.HTTPNotAcceptable,
    407: exc.HTTPProxyAuthenticationRequired,
    408: exc.HTTPRequestTimeout,
    409: exc.HTTPConflict,
    410: exc.HTTPGone,
    411: exc.HTTPLengthRequired,
    412: exc.HTTPPreconditionFailed,
    413: exc.HTTPRequestEntityTooLarge,
    414: exc.HTTPRequestURITooLong,
    415: exc.HTTPUnsupportedMediaType,
    416: exc.HTTPRequestRangeNotSatisfiable,
    417: exc.HTTPExpectationFailed,
    422: exc.HTTPUnprocessableEntity,
    423: exc.HTTPLocked,
    424: exc.HTTPFailedDependency,
    428: exc.HTTPPreconditionRequired,
    429: exc.HTTPTooManyRequests,
    431: exc.HTTPRequestHeaderFieldsTooLarge,
    451: exc.HTTPUnavailableForLegalReasons,

#HTTP Error: Server Error

    500: exc.HTTPInternalServerError,
    501: exc.HTTPNotImplemented,
    502: exc.HTTPBadGateway,
    503: exc.HTTPServiceUnavailable,
    504: exc.HTTPGatewayTimeout,
    505: exc.HTTPVersionNotSupported,
    511: exc.HTTPNetworkAuthenticationRequired,
}


GENERIC_ERROR = exc.HTTPInternalServerError(
    'The server could not handle the request nor '
    'generate a readable error.')


def reply(code, text=None, charset='utf8', content_type='text/plain'):
    if code in HTTPRESPONSES:
        if text is None:
            response = HTTPRESPONSES.get(code)
            return response()
        else:
            response = Response(
                text, status=code, content_type=content_type, charset=charset)
            return response
    return GENERIC_ERROR
