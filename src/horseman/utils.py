import typing as t
from pathlib import Path


def file_iterator(path: Path, chunk: int = 4096) -> t.Iterator[bytes]:
    with path.open('rb') as reader:
        while True:
            data = reader.read(chunk)
            if not data:
                break
            yield data


class unique:  # Originally taken from pyramid.decorator
    """Cache a property.
    Use as a method decorator.  It operates almost exactly like the
    Python ``@property`` decorator, but it puts the result of the
    method it decorates into the instance dict after the first call,
    effectively replacing the function it decorates with an instance
    variable.
    """
    def __init__(self, wrapped):
        self.wrapped = wrapped
        self.__doc__ = wrapped.__doc__

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val


# https://peps.python.org/pep-0594/
# Copied from CGI to avoid python 3.11 deprecating and python 3.13 removal
def _parseparam(s: str) -> t.Generator[str, None, None]:
    while s[:1] == ";":
        s = s[1:]
        end = s.find(";")
        while end > 0 and (s.count('"', 0, end) - s.count('\\"', 0, end)) % 2:
            end = s.find(";", end + 1)
        if end < 0:
            end = len(s)
        f = s[:end]
        yield f.strip()
        s = s[end:]


def parse_header(line: str) -> t.Tuple[str, t.Dict[str, str]]:
    """Parse a Content-type like header.
    Return the main content-type and a dictionary of options.
    """
    parts = _parseparam(";" + line)
    key = parts.__next__()
    pdict = {}
    for p in parts:
        i = p.find("=")
        if i >= 0:
            name = p[:i].strip().lower()
            value = p[i + 1:].strip()
            if len(value) >= 2 and value[0] == value[-1] == '"':
                value = value[1:-1]
                value = value.replace("\\\\", "\\").replace('\\"', '"')
            pdict[name] = value
    return key, pdict
