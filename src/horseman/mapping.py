import re
from typing import Mapping
from collections import UserDict
from horseman.meta import Node
from horseman.types import WSGICallable, Environ


class Mapping(Node, UserDict, Mapping[str, WSGICallable]):

    NORMALIZE = re.compile('//+')

    @classmethod
    def normalize(self, path: str):
        if not path.startswith('/'):
            raise ValueError(f"Path must start with '/', got {path!r}")
        return self.NORMALIZE.sub('/', path)

    def __setitem__(self, path: str, script: WSGICallable):
        super().__setitem__(self.normalize(path), script)

    def resolve(self, path_info: str, environ: Environ) -> WSGICallable:
        for script_name in sorted(self.keys(), key=len, reverse=True):
            if path_info.startswith(script_name):
                script = self[script_name]
                environ['SCRIPT_NAME'] += script_name
                environ['PATH_INFO'] = path_info[len(script_name):]
                return script