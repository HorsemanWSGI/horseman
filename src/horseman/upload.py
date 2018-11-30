# -*- coding: utf-8 -*-

import hashlib
import os
import shutil
from stat import ST_SIZE, ST_CTIME


CHUNKSIZE = 4096
INNER_ENCODING = 'utf-8'
REWIND = object()
CLOSE = object()


remove_punctuation_map = dict((
    ord(char), None) for char in '''\/\'\"*?:;"<>|'''
)
_windows_device_files = (
    'CON', 'AUX', 'COM1', 'COM2', 'COM3',
    'COM4', 'LPT1', 'LPT2', 'LPT3', 'PRN', 'NUL')


def stat_file(path):
    stats = os.stat(path)
    return stats[ST_SIZE], stats[ST_CTIME]


def chunk_reader(fobj, chunk_size=CHUNKSIZE):
    """Generator that reads a file in chunks of bytes
    """
    while True:
        chunk = fobj.read(chunk_size)
        if not chunk:
            return
        yield chunk


class FileIterable(object):

    def __init__(self, filename, filepath):
         self.filename = filename
         self.filepath = filepath

    def __iter__(self):
        with open(self.filepath, 'rb') as fd:
            for chunk in chunk_reader(fd):
                yield chunk


def digest(fobj, hash=hashlib.sha1):
    hashobj = hash()
    size = os.fstat(fobj.fileno()).st_size
    hashobj.update(b"blob %i\0" % size)
    for chunk in chunk_reader(fobj):
        hashobj.update(chunk)
    fobj.seek(0)
    return hashobj.hexdigest()


def clean_filename(filename):
    """Borrowed from Werkzeug : http://werkzeug.pocoo.org/
    """
    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, ' ')

    filename = filename.strip()

    # on nt a couple of special files are present in each folder. We
    # have to ensure that the target file is not such a filename. In
    # this case we prepend an underline
    if os.name == 'nt' and filename and \
       filename.split('.')[0].upper() in _windows_device_files:
        filename = '_' + filename

    return filename.translate(remove_punctuation_map)


def persist_files(destination, *files):
    """Document me.
    """
    # digest registry

    digests = set()

    for item in files:
        digested = digest(item.file)
        if digested not in digests:
            digests.add(digested)
            filename = clean_filename(item.filename)
            path = os.path.join(destination, filename)
            with open(path, 'wb') as upload:
                shutil.copyfileobj(item.file, upload)
            size, date = stat_file(path)
            yield (digested, filename, size, date)
