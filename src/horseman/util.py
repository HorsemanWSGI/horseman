from typing import List, Tuple, Callable
from inspect import isclass, isfunction, ismethod, getmembers

from horseman.meta import APIView
from horseman.definitions import METHODS


def view_methods(vw) -> List[Tuple[str, Callable]]:
    if isclass(vw):
        if issubclass(vw, APIView):
            predicate = lambda x: isfunction(x) and  x.__name__ in METHODS
        else:
            predicate = lambda x: (
                isfunction(x) and not x.__name__.startswith('_'))
    else:
        if isinstance(vw, APIView):
            predicate = lambda x: ismethod(x) and  x.__name__ in METHODS
        else:
            predicate = lambda x: (
                ismethod(x) and not x.__name__.startswith('_'))

    return getmembers(vw, predicate=predicate)
