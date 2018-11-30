# -*- coding: utf-8 -*-

import json
import inspect
from functools import wraps
from collections import namedtuple, Iterable

from webob import Request
from zope.schema import getFieldsInOrder, getValidationErrors
from zope.schema.interfaces import ICollection

from horseman.responder import reply
from horseman.components import BaseOverhead


def extract_fields(fields, params):
    for name, field in fields:
        value = params.get(name)
        
        if value is None:
            yield value
        elif ICollection.providedBy(field):
            if not isinstance(value, Iterable):
                value = [value]
            yield value
        else:
            if (isinstance(value, Iterable) and
                not isinstance(value, (str, bytes))):
                value = value[0]
            if hasattr(field, 'fromUnicode'):
                value = field.fromUnicode(value)
            yield value


def extract_get(environ):
    request = Request(environ)
    params = request.GET
    return params.dict_of_lists()


def extract_put(environ):
    request = Request(environ)
    if request.content_type == 'application/json':
        return request.json
    params = request.PUT
    return params.dict_of_lists()


def extract_post(environ):
    request = Request(environ)
    if request.content_type == 'application/json':
        return request.json
    params = request.POST
    return params.dict_of_lists()


class ZopeSchema:

    extractors = {
        'GET': extract_get,
        'POST': extract_post,
        'PUT': extract_put,
    }

    def __init__(self, iface, as_dict=False, *sources):
        self.iface = iface
        self.fields = getFieldsInOrder(iface)
        self.as_dict = as_dict

    def extract(self, environ):
        method = environ['REQUEST_METHOD']
        extractor = self.extractors.get(method)
        if extractor is None:
            raise NotImplementedError('No extractor for method %s' % method)
        return extractor(environ)

    def process_action(self, environ, datacls):
        params = self.extract(environ)            
        fields = list(extract_fields(self.fields, params))
        data = datacls(*fields)
        errors = getValidationErrors(self.iface, data)
        nb_errors = len(errors)
    
        if nb_errors:
            summary = {}
            for field, error in errors:
                doc = getattr(error, 'doc', error.__str__)
                field_errors = summary.setdefault(field, [])
                field_errors.append(doc())

            return reply(
                400, text=json.dumps(summary),
                content_type="application/json")

        return data

    def __call__(self, action):
        names = tuple((field[0] for field in self.fields))
        DataClass = namedtuple(action.__name__, names)

        @wraps(action)
        def method_validation(overhead):
            result = self.process_action(overhead.environ, DataClass)
            if isinstance(result, DataClass):
                if self.as_dict:
                    result = result._asdict()

                if overhead is None:
                    overhead = result
                else:
                    assert isinstance(overhead, BaseOverhead)
                    overhead.set_data(result)

                if inst is not None:
                    return action(inst, environ, overhead)
                return action(environ, overhead)

            return result
        return method_validation
