# -*- coding: utf-8 -*-
"""
Taken from
https://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html
"""

METHODS = frozenset((
    "GET",
    # Retrieves whatever data is identified by the URI, so where
    # the URI refers to a data-producing process, or a script which can
    # be run by such a process, it is this data which will be returned,
    # and not the source text of the script or process. Also used for
    # searches.

    "HEAD",
    # Similar to GET but returns only HTTP headers and no document
    # body.

    "PUT",
    # Specifies that the data in the body section is to be stored under
    # the supplied URL. The URL must already exist. The new contenst of
    # the document are the data part of the request. POST and REPLY
    # should be used for creating new documents.

    "DELETE",
    # Requests that the server delete the information corresponding to
    # the given URL. After a successfull DELETE method, the URL becomes
    # invalid for any future methods.

    "PATCH",
    # Applies a set of changes described in the request entity to the
    # resource identified by the Request-URI. The set of changes is
    # represented in a format called a "patch document" identified by a
    # media type. If the Request-URI does not point to an existing resource,
    # the server MAY create a new resource, depending on the patch.

    "POST",
    # Creates a new object linked to the specified object. The
    # message-id field of the new object may be set by the client or
    # else will be given by the server. A URL will be allocated by the
    # server and returned to the client. The new document is the data
    # part of the request. It is considered to be subordinate to the
    # specified object, in the way that a file is subordinate to a
    # directory containing it, or a news article is subordinate to a
    # newsgroup to which it is posted.

    "OPTIONS",
    # The OPTIONS method represents a request for information about the
    # communication options available on the request/response chain
    # identified by the Request-URI. This method allows the client to
    # determine the options and/or requirements associated with a
    # resource, or the capabilities of a server, without implying a
    # resource action or initiating a resource retrieval.
    # Responses to this method are not cacheable.
))
