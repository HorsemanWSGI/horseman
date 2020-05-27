import wrapt
from horseman.response import Response
from horseman.parsing import parse
from horseman.http import Multidict
from pydantic import BaseModel, ValidationError


def validate(model: BaseModel):
    @wrapt.decorator
    def model_validator(wrapped, instance, args, kwargs):
        request = args[0]
        form, files = parse(
            request.environ['wsgi.input'], request.content_type)

        if isinstance(form, Multidict):
            form = form.to_dict()
        if isinstance(files, Multidict):
            files = files.to_dict()

        try:
            item = model.parse_obj({**form, **files})
        except ValidationError as e:
            return Response.create(
                400, e.json(),
                headers={'Content-Type': 'application/json'})

        return wrapped(request, item, **kwargs)
    return model_validator
