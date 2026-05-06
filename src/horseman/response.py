from io import BytesIO
from pathlib import Path
from typing import Iterable
from horseman.abc.response import ResponseProtocol, FileResponseProtocol
from horseman.types import WSGIEnviron, WSGICallable, StartResponse, Finisher


class Response(WSGICallable, ResponseProtocol[Finisher]):

    def close(self):
        """Exhaust the list of finishers. No error is handled here.
        An exception will cause the closing operation to fail during iteration.
        """
        if self._finishers:
            while self._finishers:
                finisher = self._finishers.popleft()
                finisher(self)

    def __call__(
        self, environ: WSGIEnviron, start_response: StartResponse
    ) -> Iterable[bytes]:
        status = f"{self.status.value} {self.status.phrase}"
        start_response(status, list(self.headers.items()))
        return self


class FileWrapperResponse(WSGICallable, FileResponseProtocol):

    def __call__(self, environ: WSGIEnviron, start_response: StartResponse):
        status = f"{self.status.value} {self.status.phrase}"
        start_response(status, list(self.headers.items()))

        if isinstance(self.file_, Path):
            filelike = self.file_.open("rb")
            return environ["wsgi.file_wrapper"](filelike, self.block_size)
        elif isinstance(self.file_, BytesIO):
            return environ["wsgi.file_wrapper"](self.file_, self.block_size)

        raise TypeError(
            "Response file should be a Path or a BytesIO object.")
