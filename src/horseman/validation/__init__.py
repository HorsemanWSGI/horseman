try:
    from .json import JSONSchema
except ImportError:
    print('JSONSchema unavailable.')


try:
    from .ztk import ZopeSchema
except ImportError:
    print('Zope schema unavailable.')
