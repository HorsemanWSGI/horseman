import re
from typing import Mapping
from collections import UserDict
from horseman.meta import Node
from horseman.types import WSGICallable, Environ


class Mapping(Node, UserDict, Mapping[str, WSGICallable]):

    NORMALIZE = re.compile('//+')

    @classmethod
    def normalize(cls, path: str):
        if not isinstance(path, str):
            raise ValueError(f'{cls} accepts only str keys.')
        if not path.startswith('/'):
            raise ValueError(f"Path must start with '/', got {path!r}")
        return cls.NORMALIZE.sub('/', path)

    def __setitem__(self, path: str, script: WSGICallable):
        super().__setitem__(self.normalize(path), script)

    def resolve(self, path_info: str, environ: Environ) -> WSGICallable:
        for script_name in sorted(self.keys(), key=len, reverse=True):
            if path_info.startswith(script_name):
                script = self[script_name]
                name = script_name.rstrip('/')
                environ['SCRIPT_NAME'] += name
                environ['PATH_INFO'] = path_info[len(name):]
                return script
