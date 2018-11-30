# -*- coding: utf-8 -*-
try:
    from jsonschema import Draft4Validator
except ImportError:
    raise 
import json
from functools import wraps
from horseman.responder import reply


class JSONSchema:

    def __init__(self, schema, schema_string):
        self.string = schema_string
        self.schema = json.loads(schema_string)

    @classmethod
    def create_from_string(cls, string):
        schema = json.loads(string)
        return cls(schema, string)

    @classmethod
    def create_from_json(cls, schema):
        string = json.dumps(schema)
        return cls(schema, string)

    def validate_object(self, obj):
        errors = {}
        validator = Draft4Validator(self.schema)
        for error in sorted(validator.iter_errors(obj), key=str):
            if 'required' in error.schema_path:
                causes = ['__missing__']
            elif error.path:
                causes = error.path
            else:
                causes = ['__general__']
            for field in causes:
                fielderrors = errors.setdefault(field, [])
                fielderrors.append(error.message)
        return errors

    def __call__(self, method):
        @wraps(method)
        def validate_method(overhead):
            request = Request(overhead.environ)
            
            if request.content_type != 'application/json':
                return reply(406, text="Content type must be application/json")

            errors = self.validate_object(request.json)
            if errors:
                return reply(
                    400, text=json.dumps(errors),
                    content_type='application/json')
            overhead.set_data(request.json)
            return method(inst, environ, overhead)
        return validate_method
