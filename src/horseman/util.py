from typing import List, Tuple, Callable
from inspect import isclass, isfunction, ismethod, getmembers

from horseman.meta import View, APIView
from horseman.definitions import METHODS


def view_methods(vw) -> List[Tuple[str, Callable]]:
    if isclass(vw):
        if issubclass(vw, APIView):
            predicate = lambda x: isfunction(x) and  x.__name__ in METHODS
        elif issubclass(vw, View):
            predicate = lambda x: (
                isfunction(x) and not x.__name__.startswith('_'))
        else:
            raise NotImplementedError(
                f'{vw} must be a subclass of `horseman.meta.View`')
    else:
        if isinstance(vw, APIView):
            predicate = lambda x: ismethod(x) and  x.__name__ in METHODS
        elif isinstance(vw, View):
            predicate = lambda x: (
                ismethod(x) and not x.__name__.startswith('_'))
        else:
            raise NotImplementedError(
                f'{vw} must be an instance of `horseman.meta.View`')

    return getmembers(vw, predicate=predicate)
