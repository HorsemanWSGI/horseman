from functools import wraps
from horseman.response import Response
from horseman.parsing import parse
from voluptuous import Schema, MultipleInvalid
from collections import defaultdict
try:
    # In case you use json heavily, we recommend installing
    # https://pypi.python.org/pypi/ujson for better performances.
    import ujson as json
    JSONDecodeError = ValueError
except ImportError:
    import json as json
    from json.decoder import JSONDecodeError


class Validator:

    def __init__(self, schema):
        if not isinstance(schema, Schema):
            schema = Schema(schema)
        self.schema = schema

    def validate_object(self, obj):
        try:
            self.schema(obj)
        except MultipleInvalid as invalid:
            errors = defaultdict(list)
            for e in invalid.errors:
                key = '/'.join((str(p) for p in e.path))
                errors[key].append(e.msg)
            return errors

    def __call__(self, method):
        @wraps(method)
        def validate_method(overhead):
            form, files = parse(
                overhead.environ['wsgi.input'], overhead.content_type)
            errors = self.validate_object(form)
            if errors:
                return Response.create(
                    400, json.dumps(errors),
                    {'Content-Type': 'application/json'})
            overhead.set_data(form, files)
            return method(overhead)
        return validate_method


try:
    from voluptuary import to_voluptuous
except ImportError:
    pass
else:
    class JSONSchemaValidator(Validator):

        def __init__(self, jschema: dict):
            self.jschema = to_voluptuous(jschema)
            self.jsonschema = jschema
