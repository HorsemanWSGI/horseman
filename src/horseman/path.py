import re
import enum
from collections import deque


class Namespace(enum.Enum):
    default = 'default'
    view = 'view'


def parse_path(path, shortcuts=None):
    """Parses a path /foo/bar/baz to a stack of steps.
    A step is a ns, name tuple.
    Namespaces can be indicated with ++foo++ at the beginning of a step,
    where 'foo' is the namespace.
    By default, the namespace is considered to be `Namespace.default`.
    A dictionary of shortcuts can be supplied, where each key is a
    a character combination (such as '@@') that should be expanded,
    and the value is the namespace it should be expanded to (such as 'view').
    Shortcuts only exist for namespaces and are applied to the beginning
    of the path.
    """
    stack = deque()

    path = path.strip('/')

    if not path:
        return stack

    if shortcuts is None:
        shortcuts = {}

    steps = re.split(r'/+', path)
    for step in steps:
        for key, value in shortcuts.items():
            if step.startswith(key):
                step = ('++%s++' % value) + step[len(key):]
                break
        if step.startswith('++'):
            try:
                ns, name = step[2:].split(u'++', 1)
            except ValueError:
                ns = Namespace.default
                name = step
        else:
            ns = Namespace.default
            name = step
        stack.append((ns, name))

    return stack


def create_path(stack, shortcuts=None, default='default'):
    """Rebuilds a path from a stack.
    A dictionary of shortcuts can be supplied to minimize namespaces use
    """
    if shortcuts is None:
        shortcuts = {}
    else:
        inversed_shortcuts = {}
        for key, value in shortcuts.items():
            # do not allow multiple shortcuts for the same namespace
            assert value not in inversed_shortcuts
            inversed_shortcuts[value] = key
        shortcuts = inversed_shortcuts
    path = deque()
    for ns, name in stack:
        if ns == Namespace.default:
            path.append(name)
            continue
        shortcut = shortcuts.get(ns)
        if shortcut is not None:
            path.append(shortcut + name)
            continue
        path.append('++%s++%s' % (ns, name))
    return '/' + '/'.join(path)
