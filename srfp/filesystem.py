from fs.base import FS, NoDefaultMeta
from fs.filelike import FileLikeBase
from fs.errors import UnsupportedError, NoMetaError
from threading import Thread
from datetime import datetime
import sys
import os
import begin

import logging
logger = logging.getLogger(__name__)

try:
    from queue import Queue
except ImportError:
    from Queue import Queue

from .comms import MessageIO
from . import protocol

def proto2filename(name):
    name = [x for x in name if x]
    return os.path.join(*name)

def filename2proto(name):
    v = list(os.path.split(name))
    if v[0] == "/":
        del v[0]
    return [x for x in v if x]

class SRFPFS (FS):
    def __init__(self, address):
        self.msgio = MessageIO(address)
        self.msg_q = Queue()
        thread = Thread(target=self._process_thread)
        thread.daemon = True
        thread.start()

    def get_meta(self, meta_name, default=NoDefaultMeta):
        if meta_name == "read_only":
            return True
        if default != NoDefaultMeta:
            return default
        raise NoMetaError()

    def _process_thread(self):
        while True:
            msg_to_send, resp_q = self.msg_q.get()
            self.msgio.send_msg(msg_to_send)
            resp_q.put(self.msgio.recv_msg())
            self.msg_q.task_done()

    def _msg_get(self, msg):
        resp_q = Queue()
        self.msg_q.put((msg, resp_q))
        return resp_q.get()

    def open(self, path, mode='r', buffering=-1, encoding=None, errors=None, newline=None, line_buffering=False, **kwargs):
        logger.debug("open: %s", path)
        if 'w' in mode or 'a' in mode:
            raise UnsupportedError()

        return SRFPFile(self, filename2proto(path))

    def isfile(self, path):
        logger.debug("isfile: %s", path)
        resp = self._msg_get(protocol.NodeInfoRequest(filename2proto(path)))
        logger.debug("isfile: %s result: %s", path, resp.isfile)
        return resp.isfile

    def isdir(self, path):
        return not self.isfile(path)

    def listdir(self, path='./', wildcard=None, full=False, absolute=False, dirs_only=False, files_only=False):
        logger.debug("listdir: %s", path)
        fn_tuple = filename2proto(path)
        resp = self._msg_get(protocol.DirectoryListRequest(fn_tuple))

        # absolute doesn't make sense without full
        if absolute:
            full = True

        rv = []
        for i in resp.listing:
            if full:
                rvi = proto2filename(fn_tuple + (i,))
            else:
                rvi = i

            if absolute:
                rvi = '/' + rvi
            rv.append(rvi)
        return rv

    def makedir(self, path, recursive=False, allow_recreate=False):
        raise UnsupportedError()

    def remove(self, path):
        raise UnsupportedError()

    def removedir(self, path, recursive=False, force=False):
        raise UnsupportedError()

    def rename(self, src, dst):
        raise UnsupportedError()

    def getinfo(self, path):
        logger.debug("getinfo: %s", path)
        resp = self._msg_get(protocol.NodeInfoRequest(filename2proto(path)))
        ret = {}
        if resp.size: ret['size'] = resp.size
        if resp.created: ret['created_time'] = datetime.fromtimestamp(resp.created)
        if resp.accessed: ret['accessed_time'] = datetime.fromtimestamp(resp.accessed)
        if resp.modified: ret['modified_time'] = datetime.fromtimestamp(resp.modified)
        return ret


class SRFPFile (FileLikeBase):
    def __init__(self, fs, path):
        super(SRFPFile, self).__init__()
        self.path = path
        self.fs = fs
        self.ptr = 0

    def _read(self, sizehint=-1):
        if sizehint == -1 or sizehint > 0x0fff:
            sizehint = 0x0fff
        logger.debug("_read: ptr=%s, s=%s", self.ptr, sizehint)
        rv = self.fs._msg_get(protocol.FileContentsRequest(self.ptr, sizehint, self.path))
        returned_len = len(rv.data)
        if returned_len == 0:
            return None
        self.ptr += returned_len
        return rv.data

    def _seek(self, offset, whence):
        if whence != 0:
            raise NotImplementedError()
        self.ptr = offset

    def _tell(self):
        return self.ptr


@begin.start
@begin.logging
def start(path, mountpoint):
    myfs = SRFPFS(path)
    from fs.expose import fuse
    fuse.mount(myfs, mountpoint.encode('utf8'), foreground=True)
